from __future__ import annotations
from dataclasses import dataclass, field
from datetime import time, datetime, timedelta
from typing import List, Dict

from definition import ConversationID, Conversation, ConversationFactory, ChatID
from common import Config, OpenAIConfig
from ai.common import getOpenAIClient


from openai import APIConnectionError, APITimeoutError
from openai.types.chat import ChatCompletion, ChatCompletionMessage, ChatCompletionRole
from tiktoken import Encoding, encoding_for_model

# const
#maxMessageQueueToken = 3600
maxMessageQueueToken = 1000
CompletionTimeout    = timedelta(seconds=1)

@dataclass
class QA:
    q: str = field(default=None) # question
    a: str = field(default=None) # answer
    s: str = field(default=None) # system role




    

class OpenAITalk(Conversation):
    def __init__(self, botName: str, cfg: OpenAIConfig) -> None:
        self.botName: str = botName
        self.ctxTimeout: timedelta = timedelta(seconds=cfg.contextTimeout)
        self.lastMessage: time = None
        self.greeting = QA(
            s =  "You are a helpful assistant. Your name is %s." % self.botName
        )
        self.messageQueue: List[QA] = []
        self.model = cfg.model
        self.encoding: Encoding = encoding_for_model(self.model)
        self.client = getOpenAIClient(cfg.apiKey)

        
    
    def prepareNewMessage(self, msg: str) -> None:
        totalToken = self.getTOkenCount(msg) + self.getTOkenCount(self.greeting.s)
        now: time = datetime.now().time()
        isOld: bool = self.lastMessage is not None and now > (self.lastMessage + self.ctxTimeout)

        newQ: List[QA] = [QA(q=msg),]

        # add conversation history
        for i in range(len(self.messageQueue) -1, 0, -1):
            if totalToken >= maxMessageQueueToken or isOld:
                break
            cnt = self.getTOkenCount(self.messageQueue[i].q) + self.getTOkenCount(self.messageQueue[i].a)
            if totalToken + cnt > maxMessageQueueToken:
                break
            
            newQ.append(self.messageQueue[i])
            totalToken += cnt
        
        newQ.append(self.greeting)

        # reverse new queue
        for i in range(int(len(newQ)/2)):
            j = len(newQ) -1 -i
            newQ[i], newQ[j] = newQ[j], newQ[i] # swap
        
        self.messageQueue = newQ

    
    def getTOkenCount(self, msg: str) -> int:
        if msg is None or msg == "":
            return 0
        return len(self.encoding.encode(msg))


    def ask(self, q: str) -> str:
        self.prepareNewMessage(q)

        messages = []

        for msg in self.messageQueue:
            if msg.s is not None and msg.s != "":
                messages.append(
                    {
                        "role": "system",
                        "content": msg.s
                    }
                )
            if msg.q is not None and msg.q != "":
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
        
        retry = 3
        while retry > 0:
            try:
                resp: ChatCompletion = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    timeout=int(self.ctxTimeout.total_seconds())
                )
                answer = resp.choices[0].message.content
                if answer is not None and len(answer) > 0:
                    self.messageQueue[-1].a = answer
                    return answer
            except (APITimeoutError, APIConnectionError) as e:
                print(e)
                retry -= 1
            except Exception as e:
                print(e)
                retry -= 1
                
        return "I apologize, but the OpenAI API is currently experiencing high traffic. Kindly try again at a later time."


class TalkFactory(ConversationFactory):

    def __init__(self, config: Config) -> None:
        self.config: Config = config
        self.talks: Dict[ChatID, Conversation] = {}

    
    def getTalk(self, cid: ChatID) -> Conversation:
        if cid in self.talks:
            return self.talks[cid]
        
        talk = OpenAITalk(self.config.botName, self.config.openAI)
        self.talks[cid] = talk
        
        return talk

