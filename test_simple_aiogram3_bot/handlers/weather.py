from aiogram import Router, types, F
from utils.my_libs import get_weather
from config_set import config

allowed_ids = config.allowed_ids
open_weather_token = config.open_weather_token

async def city_weather(message: types.Message):
    await message.answer(get_weather(message.text.lower(), open_weather_token))

async def minsk_weather(callback: types.CallbackQuery):
    await callback.message.answer(get_weather(callback.data, open_weather_token))


router = Router()

def register_city_weather(router):
    router.message.register(city_weather, F.from_user.id.in_(allowed_ids),
                                          F.text.regexp(r"\b[^\d\W]+\b")) # одно слово
    router.callback_query.register(minsk_weather, F.from_user.id.in_(allowed_ids),
                                                  F.data=='minsk')
