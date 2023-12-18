from datetime import datetime, timedelta
from typing import List

import google.generativeai as genai
import PIL.Image

from common import GeminiConfig
from definition import Talk

from loguru import logger

configuredKey = None
def configureGemini(apiKey: str):
    global configuredKey
    if apiKey != configuredKey and apiKey is not None and len(apiKey) > 0:
        configuredKey = apiKey
        genai.configure(api_key=configuredKey)
        

greeting = [
    {
        'role': 'user',
        'parts': ['I will call you as Chloe.']
    },
    {
        'role': 'model',
        'parts': ['You can call me Chloe.']
    },
]

class GeminiTalk(Talk):

    def __init__(self, botName: str, config: GeminiConfig) -> None:
        self.apiKey: str = config.apiKey
        configureGemini(self.apiKey)
        self.model = genai.GenerativeModel(config.model)
        self.lastMessage = datetime.now()
        self.ctxTimeout = timedelta(seconds=config.contextTimeout)
        self.visionModel = genai.GenerativeModel(config.visionModel)
        self.pendingContent = []
        self.pendingContent.extend(greeting)
        self.hasImage = False

    def ask(self, q: str) -> str:
        now = datetime.now()
        if now > self.lastMessage + self.ctxTimeout:
            self.pendingContent = []
            self.pendingContent.extend(greeting)
            self.hasImage = False
        
        if len(self.pendingContent) > 2 and self.pendingContent[-1]['role'] == 'user':
            self.pendingContent[-1]['parts'].append(q)
        else:
            self.pendingContent.append(
                {
                    'role': 'user',
                    'parts': [q]
                }
            )
            
        try:
            if self.hasImage:
                resp = self.visionModel.generate_content(self.pendingContent[-1]) # gemini-pro-vision is not enabled for multi-turn conversation
                resp.resolve()

                self.pendingContent = []
                self.pendingContent.extend(greeting)
                self.hasImage = False

            else:
                resp = self.model.generate_content(self.pendingContent)
                resp.resolve()

                self.pendingContent.append({
                    'role': 'model',
                    'parts': [resp.text]
                })
        except Exception as e:
            logger.exception(str(e))
            
        self.lastMessage = datetime.now()
        return resp.text

    def prepareImages(self, images: List[str]=None) -> None:
        now = datetime.now()
        if now > self.lastMessage + self.ctxTimeout:
            self.pendingContent = []
            self.pendingContent.extend(greeting)
            self.hasImage = False
        
        parts = []
        for f in images:
            img = PIL.Image.open(f)
            parts.append(img)
            self.hasImage = True
        
        self.pendingContent.append(
            {
                'role': 'user',
                'parts': parts
            }
        )

        self.lastMessage = datetime.now()