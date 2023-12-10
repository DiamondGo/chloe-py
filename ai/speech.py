from definition import SpeechToText, TextToSpeech, CleanFunc
from common import rmHandle, getLogger
from ai.common import getOpenAIClient

from typing import Tuple
import os, uuid, tempfile

log = getLogger(__file__)

class Wisper(SpeechToText):
    def __init__(self, apiKey: str) -> None:
        self.client = getOpenAIClient(apiKey)
        self.requestTimeout = 30

    def convert(self, audFile: str) -> str:
        retry = 3
        while retry > 0:
            try:
                with open(audFile, "rb") as bin:
                    transcript = self.client.audio.transcriptions.create(
                        model="whisper-1",
                        file=bin,
                        timeout=self.requestTimeout
                    )
                    break
            except Exception as e:
                retry -= 1
                log.warn("speech2text request failed, %s", str(e))

        return transcript.text
        
class ReadText(TextToSpeech):
    def __init__(self, apiKey: str) -> None:
        self.client = getOpenAIClient(apiKey)
        self.requestTimeout = 30
    
    def convert(self, text: str) -> Tuple[str, CleanFunc]:
        retry = 3
        while retry > 0:
            try:
                response = self.client.audio.speech.create(
                    model="tts-1",
                    voice="nova",
                    input=text,
                    response_format="aac",
                    timeout=self.requestTimeout
                )
                break
            except Exception as e:
                log.warn("text2speech request failed, %s", str(e))
                retry -= 1
        
        filename = str(uuid.uuid4()) + ".aac"
        filepath = os.path.join(tempfile.gettempdir(), filename)
        response.stream_to_file(filepath)

        return filepath, rmHandle(filepath)