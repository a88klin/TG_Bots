from google.cloud import speech
from set.config import config
import os


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = config.GOOGLE_SERVICE_STT
client_google_STT = speech.SpeechClient()


async def stt(voice, client=client_google_STT):
    audio = speech.RecognitionAudio(content=voice.getvalue())
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.OGG_OPUS,
        sample_rate_hertz=48000,
        language_code="ru-RU")
    response = client.recognize(config=config, audio=audio)
    for result in response.results:
        return result.alternatives[0].transcript
