from datetime import datetime, timedelta
from typing import List
import time

import google.generativeai as genai
from google.generativeai import caching
import PIL.Image

from common import GeminiConfig
from definition import Talk

from loguru import logger

safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE"
    }
]

configuredKey = None
def configureGemini(apiKey: str):
    global configuredKey
    if apiKey != configuredKey and apiKey is not None and len(apiKey) > 0:
        configuredKey = apiKey
        genai.configure(api_key=configuredKey)
        
class GeminiTalk(Talk):

    def __init__(self, botName: str, config: GeminiConfig) -> None:
        self.apiKey: str = config.apiKey
        configureGemini(self.apiKey)
        
        self.initModel(config.model)
        self.lastMessage = datetime.now()
        self.ctxTimeout = timedelta(seconds=config.contextTimeout)
        self.visionModel = genai.GenerativeModel(config.visionModel)
        self.pendingContent = []
        self.greeting = [
            {
                'role': 'user',
                'parts': [f'I will call you as {botName}.']
            },
            {
                'role': 'model',
                'parts': [f'You can call me {botName}.']
            },
        ]
        self.pendingContent.extend(self.greeting)
    
    def initModel(self, model):
        self.model = genai.GenerativeModel(
            model_name=model,
            safety_settings=safety_settings
        )
        
    def expireContext(self):
        self.pendingContent = []
        self.pendingContent.extend(self.greeting)

    def ask(self, q: str) -> str:
        now = datetime.now()
        if now > self.lastMessage + self.ctxTimeout:
            self.expireContext()
        
        self.pendingContent.append(
            {
                'role': 'user',
                'parts': [q]
            }
        )
            
        retry = 3
        while retry > 0:
            try:
                resp = self.model.generate_content(self.pendingContent)
                resp.resolve()

                self.pendingContent.append({
                    'role': 'model',
                    'parts': [resp.text]
                })

                text = resp.text
                
                break
            except Exception as e:
                logger.exception(str(e))
                retry -= 1
            
        self.lastMessage = datetime.now()
        return text

    def prepareImages(self, images: List[str]=None) -> None:
        now = datetime.now()
        if now > self.lastMessage + self.ctxTimeout:
            self.expireContext()
        
        parts = self.uploadFiles(images)
        if len(parts) > 0:
            self.pendingContent.append(
                {
                    'role': 'user',
                    'parts': parts
                }
            )

        self.lastMessage = datetime.now()


    def uploadFiles(self, files: List[str]=None):
        parts = []
        for f in files:
            upload = genai.upload_file(path=f)
            while upload.state.name == 'PROCESSING':
                time.sleep(2)
                upload = genai.get_file(upload.name)
            parts.append(upload)
        return parts
 