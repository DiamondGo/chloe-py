from definition import Chat, ChatID, User, UserID

from threading import Lock
from _thread import LockType
from typing import Dict
#from dataclasses import dataclass


class ChatCache:
    
    def __init__(self) -> None:
        self.lock: LockType = Lock()
        self.chats: Dict[ChatID, Chat] = {}
        self.users: Dict[ChatID, Dict[UserID, User]] = {}
        
     
    def getChat(self, cid: ChatID) -> Chat:
        with self.lock:
            if cid in self.chats:
                return self.chats[cid]
            return None

    def cacheChat(self, cid: ChatID, chat: Chat) -> None:
        with self.lock:
            self.chats[cid] = chat
    
    def getChatUser(self, cid: ChatID, uid: UserID) -> User:
        with self.lock:
            if cid in self.users:
                if uid in self.users[cid]:
                    return self.users[cid][uid]
            return None
    
    def cacheChatUser(self, cid: ChatID, uid: UserID, user: User) -> None:
        with self.lock:
            if cid not in self.users:
                self.users[cid] = {}
            self.users[cid][uid] = user