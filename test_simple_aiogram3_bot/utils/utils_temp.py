from config_set import config
from openai import OpenAI
from openai import AsyncOpenAI
import asyncio
import g4f
import os
from io import BytesIO

# pip install SpeechRecognition
import speech_recognition as sr
# pip install pydub
from pydub import AudioSegment
# pip install gTTS
from gtts import gTTS

# pip install google-cloud-speech
from google.cloud import speech
# pip install google-cloud-texttospeech
from google.cloud import texttospeech


GPT_SECRET_KEY = config.gpt_secret_key.get_secret_value()
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'service.json'
client_google_STT = speech.SpeechClient()
client_google_TTS = texttospeech.TextToSpeechClient()
# print(client_google_TTS.list_voices(language_code='ru-RU'))


def get_answer(text):
    client = OpenAI(api_key=GPT_SECRET_KEY)
    if client:
        completion = client.chat.completions.create(
                     messages=[{"role": "user", "content": text}],
                     model="gpt-3.5-turbo")
        print(completion.choices[0].message.content)


async def get_async_answer(text):
    client = AsyncOpenAI(api_key=GPT_SECRET_KEY)
    if client:
        completion = await client.chat.completions.create(
                     messages=[{"role": "user", "content": text}],
                     model="gpt-3.5-turbo")
        print(completion.choices[0].message.content)


# gpt4free
async def get_answer_free(question:str, model='GPT35'):
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


def recognition_1(path_audio_file):
    # Преобразование файла .ogg в WAV
    ogg_audio = AudioSegment.from_ogg(path_audio_file)
    wav_audio = ogg_audio.export(f"{path_audio_file.split('.')[0]}.wav", format="wav")
    recognition = sr.Recognizer()
    with sr.AudioFile(wav_audio) as source:
        audio = recognition.record(source)  # Чтение аудиофайла
    text = recognition.recognize_google(audio, language="ru-RU")
    print(text)


def stt2(file): # not working
    # Преобразование файла .ogg в WAV
    # ogg_audio = AudioSegment.from_ogg(byte_voice)
    # wav_audio = ogg_audio.export("temp_out.wav", format="wav")
    recognition = sr.Recognizer()
    with sr.AudioFile(file) as source:
        audio = recognition.record(source)  # Чтение аудиофайла
    text = recognition.recognize_google(audio, language="ru-RU")
    print(text)


def recognition_2(path_audio_file, client=client_google_STT):
    with open(path_audio_file, "rb") as audio_file:
        content = audio_file.read()
    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.OGG_OPUS,
        sample_rate_hertz=48000,
        language_code="ru-RU")
    response = client.recognize(config=config, audio=audio)
    for result in response.results:
        print(result.alternatives[0].transcript)


def text_to_speech(text, mp3_path,
                   client=client_google_TTS,
                   language_code="ru-RU",
                   name='ru-RU-Wavenet-E',
                   speaking_rate=1):
    input_text = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
                    language_code=language_code,
                    name=name)
    audio_config = texttospeech.AudioConfig(
                    speaking_rate=speaking_rate,
                    volume_gain_db=6,
                    audio_encoding=texttospeech.AudioEncoding.MP3)
    response = client.synthesize_speech(input=input_text,
                                        voice=voice,
                                        audio_config=audio_config)
    with open(f'{mp3_path}', 'wb') as out:
        out.write(response.audio_content)


def text_to_speech2(text, mp3_path):
    tts = gTTS(text, lang='ru')
    tts.save(mp3_path)


def tts2(text):
    audio_stream = BytesIO()
    tts = gTTS(text=text, lang='ru')
    tts.write_to_fp(audio_stream)
    audio_stream.seek(0)
    return audio_stream

# *************************************

_providers = [
    g4f.Provider.Aichat,
    g4f.Provider.ChatBase,
    g4f.Provider.Bing,
    g4f.Provider.GptGo,
    g4f.Provider.You,
    g4f.Provider.Yqcloud,
]
async def run_provider(provider: g4f.Provider.BaseProvider):
    try:
        response = await g4f.ChatCompletion.create_async(
            model=g4f.models.default,
            messages=[{"role": "user", "content": "Привет, какая у тебя языковая модель ?"}],
            provider=provider,
        )
        print(f"{provider.__name__}:", response)
    except Exception as e:
        print(f"{provider.__name__}:", e)

async def run_all():
    calls = [
        run_provider(provider) for provider in _providers
    ]
    await asyncio.gather(*calls)

# ***************************************
if __name__ == "__main__":
    # asyncio.run(run_all())

    pass
    # stt2("temp_out.wav")
    # print(tts2('Привет! Какая у тебя языковая модель GPT?'))
    # get_answer('Привет. Проверяю API OpenAI')
    # asyncio.run(get_async_answer('Привет. Проверяю API OpenAI'))

    # recognition_1('temp.ogg')
    # recognition_2('temp.ogg')

    # text_to_speech('Привет! Какая у тебя языковая модель GPT?', 'temp_out.mp3')
    # text_to_speech2('Привет! Какая у тебя языковая модель GPT?', 'temp_out2.mp3')