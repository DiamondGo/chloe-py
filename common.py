from dataclasses import dataclass
import os
import yaml
import logging
from logging.handlers import TimedRotatingFileHandler
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
class TelegramConfig:
    botToken: str

@dataclass
class SystemConfig:
    whitelistEnabled: bool

@dataclass
class Config:
    botName: str
    openAI: OpenAIConfig
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
        data['telegram'] = TelegramConfig(**data['telegram'])
        data['system'] = SystemConfig(**data['system'])
        config = Config(**data)
        return config

def getAcl() -> ACL:
    with open(os.path.join(getRoot(), 'conf', 'acl.yml')) as acl:
        data = yaml.load(acl, yaml.FullLoader)
        acl = ACL(data)
        return acl


def getLogger(name) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    handler = TimedRotatingFileHandler(os.path.join(getRoot(), "log", "chloe.log"),
                                       when="midnight",
                                       interval=1,
                                       backupCount=30)
    handler.suffix = "%Y-%m-%d"

    formatter = logging.Formatter('%(asctime)s - %(message)s')
    handler.setFormatter(formatter)

    logger.addHandler(handler)

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
    