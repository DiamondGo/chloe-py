from dataclasses import dataclass
import os
import yaml
import datetime
from loguru import logger 
from typing import Callable


@dataclass
class OpenAIConfig:
    apiKey: str
    model: str
    contextTimeout: int = 120
    visionModel: str = "gpt-4-vision-preview"
    visionMaxToken: int = 300
    visionContextTimeout: int = 60

@dataclass
class GeminiConfig:
    apiKey: str
    model: str = "gemini-pro"
    contextTimeout: int = 600
    visionModel: str = "gemini-pro-vision"

@dataclass
class TelegramConfig:
    botToken: str
    escapeText: bool = False
    parseMode: str = ""

@dataclass
class SystemConfig:
    whitelistEnabled: bool
    useGemini: bool = True

@dataclass
class Config:
    botName: str
    openAI: OpenAIConfig
    gemini: GeminiConfig
    telegram: TelegramConfig
    system: SystemConfig

class ACL:
    def __init__(self, data):
        self.user = {}
        self.chat = {}

        if "allowedUserID" in data:
            uAcl = data["allowedUserID"]
            for id, allow in uAcl.items():
                self.user[id] = allow

        if "allowedChatID" in data:
            cAcl = data["allowedChatID"]
            for id, allow in cAcl.items():
                self.chat[id] = allow
    
    def allowUser(self, uid: str) -> bool:
        if uid in self.user:
            return self.user[uid]
        
        if "allow_all" in self.user:
            return self.user["allow_all"]

        return False
    
    def allowChat(self, cid: str) -> bool:
        if cid in self.chat:
            return self.chat[cid]
        
        if "allow_all" in self.chat:
            return self.chat["allow_all"]
        
        return False

def getRoot() -> str:
    return os.path.dirname(os.path.abspath(__file__))


def getConfig() -> Config:
    with open(os.path.join(getRoot(), 'conf', 'config.yml')) as cfg:
        data = yaml.load(cfg, yaml.FullLoader)
        data['openAI'] = OpenAIConfig(**data['openAI'])
        data['gemini'] = GeminiConfig(**data['gemini'])
        data['telegram'] = TelegramConfig(**data['telegram'])
        data['system'] = SystemConfig(**data['system'])
        config = Config(**data)
        return config

def getAcl() -> ACL:
    with open(os.path.join(getRoot(), 'conf', 'acl.yml')) as acl:
        data = yaml.load(acl, yaml.FullLoader)
        acl = ACL(data)
        return acl



def setLogger():
    date = datetime.datetime.now().strftime("%Y_%m_%d")
    logger.add(f"log/chloe.{date}.log", rotation="00:00", level="DEBUG", retention=30)
    return logger
    
class Defer:
    def __init__(self, *callbacks: Callable):
        self.exitFuncList = [c for c in callbacks if c is not None]
    
    def __enter__(self):
        def defer(c: Callable):
            if c is not None and callable(c):
                self.exitFuncList.append(c)
        return defer
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        for f in reversed(self.exitFuncList):
            if callable(f):
                f()

def rmHandle(f: str) -> Callable:
    def rmFunc():
        os.remove(f)
    return rmFunc
    