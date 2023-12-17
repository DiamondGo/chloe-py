from __future__ import annotations
import base64
from dataclasses import dataclass, field
from datetime import time, datetime, timedelta
from typing import List, Dict

from definition import ConversationID, Conversation, TalkFactory, ChatID, ImageRecognizer, Talk
from common import Config, OpenAIConfig
from ai.common import getOpenAIClient


from openai import APIConnectionError, APITimeoutError
from openai.types.chat import ChatCompletion, ChatCompletionMessage, ChatCompletionRole
from tiktoken import Encoding, encoding_for_model

# const
maxMessageQueueToken = 4096
#maxMessageQueueToken = 1000
CompletionTimeout    = timedelta(seconds=1)

from loguru import logger

@dataclass
class QA:
    q: str = field(default=None) # question
    a: str = field(default=None) # answer
    s: str = field(default=None) # system role
    p: str = field(default=None) # picture




    

class OpenAITalk(Talk):
    def __init__(self, botName: str, cfg: OpenAIConfig) -> None:
        self.botName: str = botName
        self.ctxTimeout: timedelta = timedelta(seconds=cfg.contextTimeout)
        self.lastMessage: datetime = None
        self.greeting = QA(
            s =  "You are a helpful assistant. Your name is %s." % self.botName
        )
        self.messageQueue: List[QA] = []
        self.model = cfg.model
        self.encoding: Encoding = encoding_for_model(self.model)
        self.client = getOpenAIClient(cfg.apiKey)
        self.requestTimeout = 30
        
        # vision process
        self.visionModel: str = cfg.visionModel
        self.visionMaxToken: int = cfg.visionMaxToken
        self.visionTimeout: timedelta = timedelta(seconds=cfg.visionContextTimeout)
    
    def getImageTokenCount(self, image: str) -> int:
        return 1024 if image is not None else 0 # I know it's not accurate
        
    def prepareNewImageMessage(self, image: str) -> None:
        totalToken = self.getTOkenCount(self.greeting.s)
        qa = QA()
        if image is not None:
            totalToken += self.getImageTokenCount(image)
            with open(image, 'rb') as img:
                qa.p = base64.b64encode(img.read()).decode('utf-8')
        
        now = datetime.now()
        isOld: bool = self.lastMessage is not None and now > (self.lastMessage + self.visionTimeout)
        
        newQ: List[QA] = [qa,]

        self.messageQueue = self.appendHistoryMessage(newQ, totalToken, isOld)
        self.lastMessage = now
    
    def prepareNewMessage(self, msg: str) -> None:
        totalToken = self.getTOkenCount(msg) + self.getTOkenCount(self.greeting.s)
        now = datetime.now()
        isOld: bool = self.lastMessage is not None and now > (self.lastMessage + self.ctxTimeout)

        for qa in self.messageQueue:
            if qa.p is not None:
                # shorter context timeout for vision request
                isOld = self.lastMessage is not None and now > (self.lastMessage + self.visionTimeout)
                break

        newQ: List[QA] = [QA(q=msg),]

        self.messageQueue = self.appendHistoryMessage(newQ, totalToken, isOld)
    
    def appendHistoryMessage(self, ql: List[QA], totalToken: int, tooOld: bool) -> List[QA]:
        # add conversation history
        for i in range(len(self.messageQueue) -1, 0, -1): # skip 0 because it's always greeting
            qa = self.messageQueue[i]
            if totalToken >= maxMessageQueueToken or tooOld:
                break
            cnt = self.getTOkenCount(qa.q) + self.getTOkenCount(qa.a) + self.getImageTokenCount(qa.p)
            if totalToken + cnt > maxMessageQueueToken:
                break
            
            ql.append(qa)
            totalToken += cnt
        
        ql.append(self.greeting)

        # reverse new queue
        for i in range(int(len(ql)/2)):
            j = len(ql) -1 -i
            ql[i], ql[j] = ql[j], ql[i] # swap
        
        return ql
        

    
    def getTOkenCount(self, msg: str) -> int:
        if msg is None or msg == "":
            return 0
        return len(self.encoding.encode(msg))


    def ask(self, q: str) -> str:
        self.prepareNewMessage(q)

        messages = []
        
        hasImage = False
        for msg in self.messageQueue:
            if msg.s is not None and msg.s != "":
                messages.append(
                    {
                        "role": "system",
                        "content": msg.s
                    }
                )
            if msg.q is not None and msg.q != "" and msg.p is None:
                messages.append(
                    {
                        "role": "user",
                        "content": msg.q
                    }
                )
            if msg.a is not None and msg.a != "":
                messages.append(
                    {
                        "role": "assistant",
                        "content": msg.a
                    }
                )
            if msg.p is not None and msg.p != "":
                hasImage = True
                if msg.q is not None and msg.q != "":
                    messages.append(
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": msg.q,
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{msg.p}"
                                    }
                                }
                            ]
                        }
                    )
                else:
                    # no text
                    messages.append(
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{msg.p}"
                                    }
                                }
                            ]
                        }
                    )
                
        
        retry = 3
        while retry > 0:
            try:
                if hasImage:
                    resp: ChatCompletion = self.client.chat.completions.create(
                        model=self.visionModel,
                        messages=messages,
                        timeout=self.requestTimeout,
                        max_tokens=maxMessageQueueToken
                    )
                else:
                    resp: ChatCompletion = self.client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        timeout=self.requestTimeout
                    )
                
                answer = resp.choices[0].message.content
                if answer is not None and len(answer) > 0:
                    self.messageQueue[-1].a = answer
                    self.lastMessage = datetime.now()
                    return answer
            except (APITimeoutError, APIConnectionError) as e:
                logger.warn("request wass likely timed out, {}", str(e))
                retry -= 1
            except Exception as e:
                logger.warn("request failed, {}", str(e))
                retry -= 1
                
        logger.error("request failed, retry run out")
        return "I apologize, but the OpenAI API is currently experiencing high traffic. Kindly try again at a later time."

    def prepareImages(self, images: List[str]=None) -> str:
        for img in images:
            self.prepareNewImageMessage(img)

class TalkFactory(TalkFactory):

    def __init__(self, config: Config) -> None:
        self.config: Config = config
        self.talks: Dict[ChatID, Talk] = {}

    
    def getTalk(self, cid: ChatID) -> Talk:
        if cid in self.talks:
            return self.talks[cid]
        
        talk = OpenAITalk(self.config.botName, self.config.openAI)
        self.talks[cid] = talk
        
        return talk

