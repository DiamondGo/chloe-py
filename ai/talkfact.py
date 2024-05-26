from definition import ConversationID, Conversation, AITalkFactory, ChatID, ImageRecognizer, Talk

from common import Config

from ai.openaitalk import OpenAITalk
from ai.geminitalk import GeminiTalk

from typing import Dict
from loguru import logger

class AITalkFactory(AITalkFactory):

    def __init__(self, config: Config) -> None:
        self.config: Config = config
        self.talks: Dict[ChatID, Talk] = {}

    
    def getTalk(self, cid: ChatID) -> Talk:
        if cid in self.talks:
            return self.talks[cid]

        if self.config.system.useGemini and self.config.gemini is not None:
            logger.debug("create gemini talk for chat {}", cid)
            talk = GeminiTalk(self.config.botName, self.config.gemini)
        else:
            logger.debug("create openai talk for chat {}", cid)
            try:
                talk = OpenAITalk(self.config.botName, self.config.openAI)
            except Exception as e:
                logger.error("fail to create openai talk, %s", str(e))
        self.talks[cid] = talk
        
        return talk

