from definition import BotService, MessageBot, Message, SpeechToText, TextToSpeech
from common import Config, ACL, Defer, getLogger
from im.tgchat import TgBot
from ai.openaitalk import TalkFactory
from ai.common import convertToMp3
from ai.speech import Wisper, ReadText

from queue import Queue
from threading import Thread
from typing import List, Iterable, Tuple

log = getLogger(__file__)
class SmartBot(BotService):

    def __init__(self, config: Config, acl: ACL) -> None:
        tgBot = TgBot(config.telegram.botToken)
        talkFact = TalkFactory(config)

        self.bots: List[MessageBot] = [tgBot]
        self.talkFactory = talkFact
        self.acl: ACL = acl
        self.s2t: SpeechToText = Wisper(config.openAI.apiKey)
        self.t2s: TextToSpeech = ReadText(config.openAI.apiKey)
        
    def listenToAll(self) -> Iterable[Message]:
        msgQ: Queue[Message] = Queue()

        def enque(bot: MessageBot):
            for msg in bot.getMessages():
                msgQ.put(msg)
        
        for bot in self.bots:
            th = Thread(target=enque, args=(bot,))
            th.start()
        
        while True:
            msg = msgQ.get()
            yield msg
    
    def isDrawRequest(self, text: str) -> Tuple[str, str]:
        return None, None

    def isMentioned(self, text: str) -> bool:
        return False


    def run(self) -> None:
        for m in self.listenToAll():
            with Defer() as defer:
                if m is None or m.getUser() is None or m.getUser().getID() is None or m.getChat() is None:
                    log.warn("received empty message, skip it")
                    if m is not None:
                        log.debug("message user is %s", m.getUser().getID())
                        log.debug("message chat is %s", m.getChat().getID())
                    continue
            
                user = m.getUser()
                uid = user.getID()
                chat = m.getChat()
                cid = chat.getID()
                voice, cleanFunc = m.getVoice()
                defer(cleanFunc)
                msgText = m.getText()
                mid = m.getID()

                allowed = self.acl.allowUser(uid)
                if not allowed:
                    allowed = self.acl.allowChat(cid)

                # routine
                memberCnt = chat.getMemberCount()
                botUsername = chat.getSelf().getUserName()

                if not allowed and memberCnt <= 2:
                    chat.replyMessage("Sorry, this AI assistant is not allowed in this conversation."+
                                    " Please contact the administrator for access.", mid)
                    log.info("access denied for user '%s' in chat '%s', message text: %s", uid, cid, msgText)
                    continue

                if voice is not None:
                    # set text to voice content
                    mp3File, cleanMp3 = convertToMp3(audioFile=voice)
                    defer(cleanMp3)

                    text = self.s2t.convert(mp3File)
                else:
                    text = msgText
                
                desc, size = self.isDrawRequest(text)
                if desc is not None and size is not None:
                    # TODO
                    pass
                    continue

                if memberCnt > 2 and not self.isMentioned(text):
                    continue

                if not allowed:
                    chat.replyMessage("Sorry, this AI assistant is not allowed in this conversation."+
                                    " Please contact the administrator for access.", mid)
                    log.info("access denied for user '%s' in chat '%s', message text: %s", uid, cid, text)
                    continue

                log.info("received question from %s, id %s: %s", user.getUserName(), uid, text)
                
                talk = self.talkFactory.getTalk(cid)
                answer = talk.ask(text)

                if voice is not None:
                    chat.quoteMessage(answer, mid, "Transcription:\n" + text)
                    vf, cleanAac = self.t2s.convert(answer)
                    defer(cleanAac)
                    if vf is not None and cleanAac is not None:
                        chat.replyVoice(vf, mid)
                        log.info("voice replied to %s", user.getUserName())
                    else:
                        log.error("failed converting to speech: %s", text)
                else:
                    chat.replyMessage(answer, mid)
                    




            