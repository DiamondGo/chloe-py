from definition import ConversationID, Conversation, AITalkFactory, ChatID, ImageRecognizer, Talk

from common import Config

from ai.openaitalk import OpenAITalk
from ai.geminitalk import GeminiTalk

from typing import Dict

class AITalkFactory(AITalkFactory):

    def __init__(self, config: Config) -> None:
        self.config: Config = config
        self.talks: Dict[ChatID, Talk] = {}

    
    def getTalk(self, cid: ChatID) -> Talk:
        if cid in self.talks:
            return self.talks[cid]

        if self.config.system.useGemini and self.config.gemini is not None:
            talk = GeminiTalk(self.config.botName, self.config.gemini)
        else:
            talk = OpenAITalk(self.config.botName, self.config.openAI)
        self.talks[cid] = talk
        
        return talk

