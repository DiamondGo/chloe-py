from __future__ import annotations

from definition import MessageBot, Message, Media, MessageID, User, UserID, Chat, ChatID, CleanFunc
from im.common import ChatCache
from common import rmHandle, getLogger

import os, tempfile, re
from queue import Queue
from threading import Thread
from telebot import TeleBot, types
from typing import Iterable, Tuple, List

log = getLogger(__file__)

_idPrefix = 'tg-'

class TgBot(MessageBot):
    
    def __init__(self, token: str) -> None:
        self.token: str = token
        self.msgQueue: Queue[types.Message] = Queue()

        self.api: TeleBot = TeleBot(self.token)
        @self.api.message_handler(content_types=['audio', 'photo', 'voice', 'text']) #, 'video', 'document', 'location', 'contact', 'sticker', 'picture'])
        def enQueue(message: types.Message) -> None:
            self.msgQueue.put(message)

        self.task: Thread = Thread(target=self.api.infinity_polling)
        self.task.start()
        self.cache: ChatCache = ChatCache()

    def getMessages(self) -> Iterable[Message]:
        while True:
            tgMsg: types.Message = self.msgQueue.get()
            msg: Message = self.tgMessageConvert(tgMsg)
            if msg is not None:
                yield msg
    
    def stripPrefixToInt(self, id: str) -> int:
        if id.startswith(_idPrefix):
            id = id[len(_idPrefix):]
        return int(id)
    
    def lookupChat(self, cid: ChatID) -> Chat:
        chat: Chat = self.cache.getChat(cid)
        if chat is not None:
            return chat
        
        #tgChat: types.Chat = self.bot.get_chat(cid)
        memberCnt: int = self.api.get_chat_member_count(self.stripPrefixToInt(cid))
        chat = TgChat(self, cid, memberCnt)
        self.cache.cacheChat(cid, chat)

        return chat
    
    def lookupUser(self, uid: UserID, cid: ChatID) -> User:
        user: User = self.cache.getChatUser(cid, uid)
        if user is not None:
            return user
        
        tgUser: types.ChatMember = self.api.get_chat_member(self.stripPrefixToInt(cid), self.stripPrefixToInt(uid))
        user = TgUser(uid, cid, tgUser.user.username, tgUser.user.first_name)
        self.cache.cacheChatUser(cid, uid, user)

        return user

    
    def tgMessageConvert(self, tgMsg: types.Message) -> Message:
        msg = TgMessage(self,
                        MessageID(_idPrefix + str(tgMsg.message_id)),
                        UserID(_idPrefix + str(tgMsg.from_user.id)),
                        ChatID(_idPrefix + str(tgMsg.chat.id)))
        msg.withText(tgMsg.text)
        if tgMsg.voice is not None or tgMsg.audio is not None:
            # save file to tmp
            if tgMsg.voice is not None:
                fd: str = tgMsg.voice.file_id
            else:
                fd: str = tgMsg.audio.file_id
            fp, cleanFunc = self.downloadFile(fd)
            msg.withAudio(fp, cleanFunc)
        if tgMsg.photo is not None:
            # get the largest latest image
            fd: str = tgMsg.photo[-1].file_id
            fp, cleanFunc = self.downloadFile(fd)
            msg.withPhoto(fp, cleanFunc)
            if tgMsg.caption is not None:
                msg.withText(tgMsg.caption)

        return msg
    
    def downloadFile(self, fd: str) -> Tuple[str, CleanFunc]:
        file_info: types.File = self.api.get_file(fd)
        ext = os.path.splitext(file_info.file_path)[-1]
        binary: bytes = self.api.download_file(file_info.file_path)
        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmpf:
            tmpf.write(binary)
            #def clean():
            #    os.remove(tmpf.name)
            return tmpf.name, rmHandle(tmpf.name)
        

class TgMedia(Media):
    def __init__(self):
        self.text = None
        self.voice = None
        self.photo = None

    def addText(self, text: str):
        if text is not None:
            if self.text is None:
                self.text = []
            self.text.append(text)
    
    def addVoice(self, audioFile: str, cleanFunc: CleanFunc):
        if audioFile is not None and cleanFunc is not None:
            if self.voice is None:
                self.voice = []
            self.voice.append((audioFile, cleanFunc))

    def addPhoto(self, photoFile: str, cleanFunc: CleanFunc):
        if photoFile is not None and cleanFunc is not None:
            if self.photo is None:
                self.photo = []
            self.photo.append((photoFile, cleanFunc))

    def getPhoto(self) -> List[Tuple[str, CleanFunc]]:
        return self.photo

    def getVoice(self) -> List[Tuple[str, CleanFunc]]:
        return self.voice
    
    def getText(self) -> List[str]:
        return self.text



class TgMessage(Message):
    
    def __init__(self, bot: TgBot, mid: MessageID, uid: UserID, cid: ChatID) -> None:
        self.bot: TgBot = bot
        self.mid: MessageID = mid
        self.uid: UserID = uid
        self.cid: ChatID = cid
        self.text: str = None
        self.audioFile: str = None
        self.cleanAudio: CleanFunc = None
        #self.photoFile: str = None
        #self.cleanPhoto: CleanFunc = None
        self.photo: List[Tuple[str, CleanFunc]] = []
        self.media: TgMedia = TgMedia()

    
    def withText(self, text: str) -> TgMessage:
        self.media.addText(text)
        return self

    def withAudio(self, filePath: str, cleanFunc: CleanFunc) -> TgMessage:
        self.media.addVoice(filePath, cleanFunc)
        return self

    def withPhoto(self, filePath: str, cleanFunc: CleanFunc) -> TgMessage:
        self.media.addPhoto(filePath, cleanFunc)
        return self

    def getID(self) -> MessageID:
        return self.mid
        
    def getUser(self) -> User:
        return self.bot.lookupUser(self.uid, self.cid)
    
    def getChat(self) -> Chat:
        return self.bot.lookupChat(self.cid)
    
    def getMedia(self) -> Media:
        return self.media
    
 

class TgChat(Chat):

    def __init__(self, bot: TgBot, id: ChatID, memberCnt: int) -> None:
        self.id: ChatID = id
        self.bot: TgBot = bot
        self.memberCount: int = memberCnt
        self.notouchPattens = self.createPatterns()
        
    def createPatterns(self) -> List[re.Pattern]:
        pattens: List[re.Pattern] = []

        codePat = re.compile(r'```.+?```', re.MULTILINE | re.DOTALL)
        pattens.append(codePat)

        emphasized = re.compile(r'`[\\.+*\(\)\-\[\]=\s\w]+`')
        pattens.append(emphasized)
        
        return pattens


    def getID(self) -> ChatID:
        return self.id

    def getMemberCount(self) -> int:
        return self.memberCount

    def sendMessage(self, message: str) -> None:
        raise NotImplementedError("not implemented")

    def replyMessage(self, message: str, replyTo: MessageID) -> None:
        escapedMsg = self.escape(message)
        if escapedMsg != message:
            log.debug("escaped message: %s", escapedMsg)
            
        try:
            self.bot.api.send_message(
                chat_id=self.bot.stripPrefixToInt(self.id),
                text=escapedMsg,
                parse_mode="MarkdownV2",
                reply_to_message_id=self.bot.stripPrefixToInt(replyTo)
            )
        except Exception as e:
            log.error("failed to send message as markdown, %s", str(e))
            self.bot.api.send_message(
                chat_id=self.bot.stripPrefixToInt(self.id),
                text=message,
                parse_mode="",
                reply_to_message_id=self.bot.stripPrefixToInt(replyTo)
            )



    def quoteMessage(self, message: str, replyTo: MessageID, quote: str) -> None:
        try:
            md = "_*" + self.escape(quote) + "*_"
            md += "  \n"
            md += "  \n"
            md += self.escape(message)

            self.bot.api.send_message(
                chat_id=self.bot.stripPrefixToInt(self.id),
                text=md,
                parse_mode="MarkdownV2",
                reply_to_message_id=self.bot.stripPrefixToInt(replyTo)
            )
        except Exception as e:
            log.error("failed to send quote message as markdown, %s", str(e))

            plain = quote
            plain += "  \n"
            plain += "  \n"
            plain += message

            self.bot.api.send_message(
                chat_id=self.bot.stripPrefixToInt(self.id),
                text=plain,
                parse_mode="",
                reply_to_message_id=self.bot.stripPrefixToInt(replyTo)
            )


    def replyImage(self, imgPath: str, message: MessageID) -> None:
        raise NotImplementedError("not implemented")
    
    def replyVoice(self, audPath: str, message: MessageID) -> None:
        with open(audPath, "rb") as voice:
            self.bot.api.send_voice(
                chat_id=self.bot.stripPrefixToInt(self.id),
                voice=voice
            )
    
    def getSelf(self) -> User:
        sid = UserID(_idPrefix +str(self.bot.api.user.id))
        return self.bot.lookupUser(sid, self.id)
    
    def escapePuncs(self, msg: str) -> str:
        escape_chars = r'_*[]()~`>#+-=|{}.!'
        return "".join('\\' + ch if ch in escape_chars else ch for ch in msg)
    
    def escapeBackslash(self, msg: str) -> str:
        return msg.replace('\\', '\\\\')
    
    def escape(self, msg: str) -> str:
        matchPos = []
        for p in self.notouchPattens:
            for m in re.finditer(p, msg):
                if m.end() > m.start():
                    matchPos.append((m.start(), m.end()))

        orderedPos = sorted(matchPos, key=lambda p: (p[0], -p[1]))

        idx = 0
        while idx < len(orderedPos) - 1:
            p1 = orderedPos[idx]
            p2 = orderedPos[idx +1]
            if p2[0] >= p1[1]:
                idx += 1
                continue

            end = max(p1[1], p2[1])
            p = (p1[0], end)
            orderedPos = orderedPos[:idx] + [p] + orderedPos[idx+2:]
        
        escaped = []
        idx = 0
        for start, end in orderedPos:
            if start > idx:
                escaped.append(self.escapePuncs(msg[idx:start]))
            escaped.append(self.escapeBackslash(msg[start:end]))
            idx = end
        if idx < len(msg):
            escaped.append(self.escapePuncs(msg[idx:]))

        return ''.join(escaped)

class TgUser(User):

    def __init__(self, id: UserID, cid: ChatID, username: str, firstname: str) -> None:
        self.id = id
        self.cid = cid
        self.username = username
        self.firstname = firstname

    def getID(self) -> UserID:
        return self.id

    def getFirstName(self) -> str:
        return self.firstname

    def getUserName(self) -> str:
        return self.username

