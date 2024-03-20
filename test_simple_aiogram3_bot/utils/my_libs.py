import math
from datetime import datetime, date
import ephem  # pip install pyephem
import g4f    # pip install g4f
import requests
import speech_recognition as sr  # pip install SpeechRecognition
from pydub import AudioSegment  # pip install pydub


# BINANCE Tickers **********************************************************
def get_server_time():
    url = 'https://api.binance.com/api/v3/time'
    timestamp = requests.get(url).json()['serverTime'] / 1000
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')


def coins_price():
    base_url = 'https://api.binance.com/api/v3/ticker/price?symbols=' \
               '[%22BTCUSDT%22,%22ETHUSDT%22,%22BNBUSDT%22]'
    str_ = f'{get_server_time()}\n\n'
    data = requests.get(url=base_url).json()
    for ticker in data:
        str_ += f"{ticker['symbol']}:  {float(ticker['price']):,.2f}\n"
    return str_


# MOON ***********************************************************************
def n_day_today():
    str_ = str(date.today().strftime("%d%m%Y"))
    s = 0
    for el in str_:
        s += int(el)
    return s if s < 10 \
        else s % 9 or \
             (9 if s % 9 == 0 else s % 9)


def get_moon(date):
    d = ephem.Date(date)
    pnm = ephem.previous_new_moon(d)
    nnm = ephem.next_new_moon(d)
    pfm = ephem.previous_full_moon(d)
    nfm = ephem.next_full_moon(d)
    md = d - pnm
    phase = None
    l = [('Date_Now', d.datetime().strftime('%Y.%m.%d - %H:%M')),
         ('Prev_nm', pnm.datetime().strftime('%Y.%m.%d - %H:%M')),
         ('Next_nm', nnm.datetime().strftime('%Y.%m.%d - %H:%M')),
         ('Prev_fm', pfm.datetime().strftime('%Y.%m.%d - %H:%M')),
         ('Next_fm', nfm.datetime().strftime('%Y.%m.%d - %H:%M'))]
    l = sorted(l, key=lambda x: x[1], reverse=False)
    if l[1][0] == 'Prev_nm' and l[3][0] == 'Next_fm':
        phase = f'{round(((d - pnm) / (nfm - pnm)), 3)} +++'
    if l[1][0] == 'Prev_fm' and l[3][0] == 'Next_nm':
        phase = f'{round(((pfm - d) / (nnm - pfm) + 1), 3)} ---'
    return phase, d, md, pnm, nnm, pfm, nfm, l


def moon_and_nday():
    d = datetime.utcnow()
    moon = get_moon(d)
    string = f'\n{date.today()} (UTC) N_Day: {n_day_today()}\n'
    string += f'Phase: {moon[0]}\n'
    string += f'Moon_Day: {math.ceil(moon[2])}\n'
    l = moon[7]
    for el in l:
        string += f'\n{el[0]}: {el[1]}'
    return string


# Single number *****************************************************************
def n10(str_):
    try:
        s = 0
        for el in str_:
            s += int(el)
        return s if s < 10 \
            else s % 9 or \
                 (9 if s % 9 == 0 else s % 9)
    except:
        return None


# Chat_GPT ***************************************************************
async def ask_gpt(question, model='GPT35'):
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


# Openweathermap.org **************************************************************
def get_weather(city, open_weather_token):
    # https://home.openweathermap.org/api_keys
    code_to_smile = {"Clear": "Ясно \U00002600",
                     "Clouds": "Облачно \U00002601",
                     "Rain": "Дождь \U00002614",
                     "Drizzle": "Дождь \U00002614",
                     "Thunderstorm": "Гроза \U000026A1",
                     "Snow": "Снег \U0001F328",
                     "Mist": "Туман \U0001F32B"}
    try:
        r = requests.get(
            f"http://api.openweathermap.org/data/2.5/weather?"
            f"q={city}&appid={open_weather_token}&units=metric")
        data = r.json()
        city = data["name"]
        cur_weather = data["main"]["temp"]
        weather_description = data["weather"][0]["main"]
        if weather_description in code_to_smile:
            wd = code_to_smile[weather_description]
        else:
            wd = "Не пойму что там за погода!"
        humidity = data["main"]["humidity"]
        pressure = data["main"]["pressure"]
        wind = data["wind"]["speed"]
        sunrise_timestamp = datetime.fromtimestamp(data["sys"]["sunrise"])
        sunset_timestamp = datetime.fromtimestamp(data["sys"]["sunset"])
        length_of_the_day = datetime.fromtimestamp(data["sys"]["sunset"]) - \
                            datetime.fromtimestamp(data["sys"]["sunrise"])
        str_ = f"***{datetime.now().strftime('%Y-%m-%d %H:%M')}***\n"
        str_ += f"Погода в городе: {city}\n"
        str_ += f"Температура: {cur_weather}C° {wd}\n"
        str_ += f"Влажность: {humidity}%\n"
        str_ += f"Давление: {pressure} мм.рт.ст\n"
        str_ += f"Ветер: {wind} м/с\n"
        str_ += f"Восход солнца: {str(sunrise_timestamp)[-8:]}\n"
        str_ += f"Закат солнца: {str(sunset_timestamp)[-8:]}\n"
        str_ += f"Продолжительность дня: {length_of_the_day}\n"
        return str_
    except Exception as ex:
        print(ex)
        return 'What are you typing... ???'


# STT **************************************************************
def stt_free(voice):  # Вызов: stt_free(BytesIO format))
    ogg_audio = AudioSegment.from_ogg(voice)
    wav_audio = ogg_audio.export(format="wav") # из .ogg в .wav
    recognition = sr.Recognizer()
    with sr.AudioFile(wav_audio) as source:
        audio = recognition.record(source)  # Чтение .wav (.ogg не читает)
    text = recognition.recognize_google(audio, language="ru-RU")
    return text
