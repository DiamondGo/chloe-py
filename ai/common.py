import os
import subprocess
from typing import Tuple

from openai import OpenAI

from definition import CleanFunc
from common import getLogger, rmHandle

log = getLogger(__file__)

def getOpenAIClient(apiKey: str) -> OpenAI:
    return OpenAI(api_key=apiKey)

def convertToMp3(audioFile: str) -> Tuple[str, CleanFunc]:
    name, ext = os.path.splitext(audioFile)
    mp3file = name + ".mp3"

    command = [
		"ffmpeg",
		"-i",
		audioFile,
		"-vn",
		"-ar",
		"44100",
		"-ac",
		"2",
		"-ab",
		"192k",
		"-f",
		"mp3",
		mp3file
	]

    with open(os.devnull, 'w') as devnull:
        result = subprocess.run(command, stdout=devnull, stderr=devnull)

    if result.returncode != 0 or not os.path.exists(mp3file):
        log.error("failed to convert %s to mp3, error code %d", audioFile, result.returncode)
        return None, None
    
    return mp3file, rmHandle(mp3file)
    

