from definition import BotService, MessageBot, Message, SpeechToText, TextToSpeech, UserID
from common import Config, ACL, Defer, getLogger
from im.tgchat import TgBot
from ai.openaitalk import TalkFactory
from ai.common import convertToMp3
from ai.speech import Wisper, ReadText

from queue import Queue
from threading import Thread, Semaphore, Lock
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Iterable, Tuple

log = getLogger(__file__)

puncs = [",", ".", "，", "。", "!", "?", "！", "？"]

class SmartBot(BotService):

    def __init__(self, config: Config, acl: ACL) -> None:
        tgBot = TgBot(config.telegram.botToken)
        talkFact = TalkFactory(config)

        self.botName = config.botName
        self.bots: List[MessageBot] = [tgBot]
        self.talkFactory = talkFact
        self.acl: ACL = acl
        self.s2t: SpeechToText = Wisper(config.openAI.apiKey)
        self.t2s: TextToSpeech = ReadText(config.openAI.apiKey)

        self.sem = Semaphore(4)
        self.glock = Lock()
        self.ulocks: Dict[UserID, Lock] = {}
        self.pool: ThreadPoolExecutor = ThreadPoolExecutor(max_workers=8)
        
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

    def isMentioned(self, text: str, botUsername: str) -> bool:
        tokens = text.split()
        tokens = spliteByPunctuation(tokens)

        if listContains(tokens, "@" + botUsername, False):
            return True
        
        head = tokens[:3]
        
        return listContains(head, self.botName, True)

    def getUserLock(self, uid: UserID) -> Lock:
        with self.glock:
            if uid in self.ulocks:
                return self.ulocks[uid]
            else:
                ul = Lock()
                self.ulocks[uid] = ul
                return ul
    
    def handleMessage(self, m: Message) -> None:
        with Defer() as defer:
            if m is None or m.getUser() is None or m.getUser().getID() is None or m.getChat() is None:
                log.warn("received empty message, skip it")
                if m is not None:
                    log.debug("message user is %s", m.getUser().getID())
                    log.debug("message chat is %s", m.getChat().getID())
                return
        
            user = m.getUser()
            uid = user.getID()
            
            lock = self.getUserLock(uid)
            lock.acquire()
            def unlock(l: Lock):
                def inner():
                    l.release()
                return inner
            defer(unlock(lock))

            self.sem.acquire()
            def release(s: Semaphore):
                def inner():
                    s.release()
                return inner
            defer(release(self.sem))

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
                return

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
                return

            if memberCnt > 2 and not self.isMentioned(text, botUsername):
                return

            if not allowed:
                chat.replyMessage("Sorry, this AI assistant is not allowed in this conversation."+
                                " Please contact the administrator for access.", mid)
                log.info("access denied for user '%s' in chat '%s', message text: %s", uid, cid, text)
                return

            log.info("received question from %s, id %s: %s", user.getUserName(), uid, text)
            
            talk = self.talkFactory.getTalk(cid)
            answer = talk.ask(text)
            log.debug("received answer for chat %s: %s", cid, answer)

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
                log.info("voice replied to %s", user.getUserName())
                

    def run(self) -> None:
        for m in self.listenToAll():
            #self.handleMessage(m)
            self.pool.submit(self.handleMessage, m)
            


            
def removePunctuation(s: str) -> str:
    for p in puncs:
        s = s.replace(p, "")
    return s

def listContains(ss: List[str], target: str, ignoreCase: bool) -> bool:
    for s in ss:
        nops = removePunctuation(s)
        if target == nops or (ignoreCase and target.lower() == nops.lower()):
            return True
    
    return False


def spliteByPunctuation(ss: List[str]) -> List[str]:
    for p in puncs:
        newSs = []
        for s in ss:
            sp = s.split(p)
            newSs.extend(sp)
        ss = newSs
    
    return [s for s in ss if s != ""]

