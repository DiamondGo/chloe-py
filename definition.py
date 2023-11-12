from abc import ABC, abstractmethod
from typing import Callable, Tuple, Iterable

ChatID = str
UserID = str
MessageID = str
CleanFunc = Callable[[], None]

class Chat(ABC):

    @abstractmethod
    def getID(self) -> ChatID:
        raise NotImplementedError("not implemented")

    @abstractmethod
    def getMemberCount(self) -> int:
        raise NotImplementedError("not implemented")

    @abstractmethod
    def sendMessage(self, message: str) -> None:
        raise NotImplementedError("not implemented")

    @abstractmethod
    def replyMessage(self, message: str, replyTo: MessageID) -> None:
        raise NotImplementedError("not implemented")

    @abstractmethod
    def quoteMessage(self, message: str, replyTo: MessageID, quote: str) -> None:
        raise NotImplementedError("not implemented")

    @abstractmethod
    def replyImage(self, imgPath: str, message: MessageID) -> None:
        raise NotImplementedError("not implemented")
    
    @abstractmethod
    def replyVoice(self, audPath: str, message: MessageID) -> None:
        raise NotImplementedError("not implemented")
    
    @abstractmethod
    def getSelf(self) -> UserID:
        raise NotImplementedError("not implemented")
    

class User(ABC):

    @abstractmethod
    def getID(self) -> UserID:
        raise NotImplementedError("not implemented")

    @abstractmethod
    def getFirstName(self) -> str:
        raise NotImplementedError("not implemented")

    @abstractmethod
    def getUserName(self) -> str:
        raise NotImplementedError("not implemented")

class Message(ABC):
    
    @abstractmethod
    def getID(self) -> MessageID:
        raise NotImplementedError("not implemented")
        
    @abstractmethod
    def getUser(self) -> UserID:
        raise NotImplementedError("not implemented")
    
    @abstractmethod
    def getChat(self) -> ChatID:
        raise NotImplementedError("not implemented")
    
    @abstractmethod
    def getText(self) -> str:
        raise NotImplementedError("not implemented")
        
    @abstractmethod
    def getVoice(self) -> Tuple[str, CleanFunc]:
        raise NotImplementedError("not implemented")
        

class MessageBot(ABC):
    
    @abstractmethod
    def getMessages(self) -> Iterable[Message]:
        raise NotImplementedError("not implemented")
     

### AI interfaces

ConversationID = int # int64 actually


class Conversation(ABC):
    
    @abstractmethod
    def getID(self) -> ConversationID:
        raise NotImplementedError("not implemented")

    @abstractmethod
    def ask(self) -> str:
        raise NotImplementedError("not implemented")


class ConversationFactory(ABC):

    @abstractmethod
    def getTalk(self, cid: ChatID) -> Conversation:
        raise NotImplementedError("not implemented")


class SpeechToText(ABC):
    
    @abstractmethod
    def convert(self, audFile: str) -> str:
        raise NotImplementedError("not implemented")


class TextToSpeech(ABC):
    
    @abstractmethod
    def convert(self, text: str) -> Tuple[str, CleanFunc]:
        raise NotImplementedError("not implemented")


class ImageGenerator(ABC):
    
    @abstractmethod
    def generate(self, desc: str, size: str) -> Tuple[str, CleanFunc]:
        raise NotImplementedError("not implemented")


### for service

class BotService(ABC):
    
    @abstractmethod
    def run(self) -> None:
        raise NotImplementedError("not implemented")