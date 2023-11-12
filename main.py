

from dataclasses import dataclass
import os
import yaml

@dataclass
class OpenAIConfig:
    apiKey: str
    model: str
    contextTimeout: int

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

def getConfig() -> Config:
    with open(os.path.join(getRoot(), 'conf', 'config.yml')) as cfg:
        data = yaml.load(cfg, yaml.FullLoader)
        data['openAI'] = OpenAIConfig(**data['openAI'])
        data['telegram'] = TelegramConfig(**data['telegram'])
        data['system'] = SystemConfig(**data['system'])
        config = Config(**data)
        return config

def getRoot() -> str:
     return os.path.dirname(os.path.abspath(__file__))


if __name__ == '__main__':
    cfg = getConfig()
    print(getRoot())