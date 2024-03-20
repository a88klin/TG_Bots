from config_set import config
from openai import AsyncOpenAI
import os
from io import BytesIO
import g4f  # https://github.com/xtekky/gpt4free
from google.cloud import speech  # pip install google-cloud-speech
from google.cloud import texttospeech  # pip install google-cloud-texttospeech
from gtts import gTTS  # pip install gTTS
import speech_recognition as sr  # pip install SpeechRecognition
from pydub import AudioSegment  # pip install pydub


GPT_SECRET_KEY = config.gpt_secret_key.get_secret_value()
gpt_client = AsyncOpenAI(api_key=GPT_SECRET_KEY)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'service.json'
client_google_STT = speech.SpeechClient()
client_google_TTS = texttospeech.TextToSpeechClient()


# OpenAI.
async def get_answer(text, client=gpt_client):
    if client:
        completion = await client.chat.completions.create(
                     messages=[{"role": "user", "content": text}],
                     model="gpt-3.5-turbo")
        return completion.choices[0].message.content


# gpt4free
async def get_answer_free(question, model='GPT35'):
    try:
        models = {'GPT35': g4f.models.gpt_35_turbo,
                  'GPT4':  g4f.models.gpt_4}
        response = await g4f.ChatCompletion.create_async(
                   model=models[model],
                   messages=[{"role": "user", "content": question}])
        response = 'Error with the response...' if '<!DOCTYPE html>' in response else response
        return response
    except:
        return 'Error with the response...'


def stt(voice, client=client_google_STT):
    audio = speech.RecognitionAudio(content=voice.getvalue())
    config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.OGG_OPUS,
            sample_rate_hertz=48000,
            language_code="ru-RU")
    response = client.recognize(config=config, audio=audio)
    for result in response.results:
        return result.alternatives[0].transcript


def stt_free(voice):  # Вызов: stt_free(BytesIO(byte_voice))
    ogg_audio = AudioSegment.from_ogg(voice)
    wav_audio = ogg_audio.export(format="wav") # из .ogg в .wav
    recognition = sr.Recognizer()
    with sr.AudioFile(wav_audio) as source:
        audio = recognition.record(source)  # Чтение .wav (.ogg не читает)
    text = recognition.recognize_google(audio, language="ru-RU")
    return text


def tts(text, client=client_google_TTS):
    input_text = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
                    language_code="ru-RU",
                    name='ru-RU-Wavenet-E')
    audio_config = texttospeech.AudioConfig(
                    speaking_rate=1,
                    volume_gain_db=6,
                    audio_encoding=texttospeech.AudioEncoding.MP3)
    response = client.synthesize_speech(input=input_text,
                                        voice=voice,
                                        audio_config=audio_config)
    # with open('file.mp3', 'wb') as out:
    #     out.write(response.audio_content)
    return response.audio_content


def tts_free(text):
    audio_stream = BytesIO()
    tts = gTTS(text=text, lang='ru')
    tts.write_to_fp(audio_stream)
    audio_stream.seek(0)
    return audio_stream
