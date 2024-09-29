from langchain_core.tools import tool
from datetime import datetime, timedelta
import requests
from set.config import config


open_weather_token = config.OPEN_WEATHER_TOKEN.get_secret_value()


@tool
def get_weather(city: str) -> str:
    """
    Функция получения текущей даты, времени, и погоды в городе {city} в настоящий момент.
    Args: city (str) - название города
    return: (str) - дата, время и теущая погода в настоящий момент
    """
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
        str_ = f"***{(datetime.now() + timedelta(hours=3)).strftime('%Y-%m-%d %H:%M')}***\n"
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
        return ex


@tool
def get_weather_forecast(city: str) -> str:
    """
    Функция получения текущей даты и времени,
    и прогноза погоды в городе {city} на 5 дней вперед с интервалом 3 часа
    Args: city (str) - название города
    return: (str) - дата, время, прогноз погоды
    """
    url = 'http://api.openweathermap.org/data/2.5/forecast'
    params = {'lang': 'ru',
              'q': city,
              'units': 'metric',
              'appid': open_weather_token}
    forecasts = []
    try:
        dt_now = (datetime.now() + timedelta(hours=3)
                  ).strftime("%Y-%m-%d %H:%M")
        r = requests.get(url=url, params=params)
        for item in r.json()['list']:
            day_time = ''
            time_forecast = datetime.fromtimestamp(
                item['dt']) + timedelta(hours=3)
            day_time += f"Прогноз на {time_forecast}\n"
            day_time += f"Температура: {item['main']['temp']} C° {item['weather'][0]['description']}\n"
            day_time += f"Влажность: {item['main']['humidity']} %\n"
            day_time += f"Давление: {item['main']['pressure']} мм.рт.ст.\n"
            day_time += f"Ветер: {item['wind']['gust']} м/с\n"
            forecasts.append(day_time)
        return f'Дата и время сейчас: {dt_now}.\n' + '#\n'.join(forecasts)
    except Exception as ex:
        return f'Service temporary unavailable: {ex}'
