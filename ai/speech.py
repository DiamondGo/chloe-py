from definition import SpeechToText, TextToSpeech, CleanFunc
from common import rmHandle
from ai.common import getOpenAIClient

from typing import Tuple
import os, uuid, tempfile

class Wisper(SpeechToText):
    def __init__(self, apiKey: str) -> None:
        self.client = getOpenAIClient(apiKey)

    def convert(self, audFile: str) -> str:
        with open(audFile, "rb") as bin:
            transcript = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=bin
            )

        return transcript.text
        
class ReadText(TextToSpeech):
    def __init__(self, apiKey: str) -> None:
        self.client = getOpenAIClient(apiKey)
    
    def convert(self, text: str) -> Tuple[str, CleanFunc]:
        response = self.client.audio.speech.create(
            model="tts-1",
            voice="nova",
            input=text,
            response_format="aac"
        )
        
        filename = str(uuid.uuid4()) + ".aac"
        filepath = os.path.join(tempfile.gettempdir(), filename)
        response.stream_to_file(filepath)

        return filepath, rmHandle(filepath)