import aiohttp
from aiogram.types import Message
from set.config import config 
BASE_URL = config.BASE_URL


# Текстовые запросы к API
async def base_request(url: str, data: dict, method: str):
    async with aiohttp.ClientSession() as session:
        if method == "GET":
            async with session.get(url, json=data) as response:
                return await response.json()
        if method == "POST":
            async with session.post(url, json=data) as response:
                return await response.json()


# Пересылка аудио файла .ogg через POST запрос API
async def post_audio_ogg(url: str, message: Message):
    async with aiohttp.ClientSession() as session:
        with open(f"D:/Download/Temp/voice_{message.from_user.id}.ogg", 'rb') as file_content:
            data = aiohttp.FormData()
            data.add_field(name='file',
                           value=file_content, 
                           content_type='audio/ogg', 
                           filename=f'{message.from_user.id}.ogg') # здесь имя - это tg_id
            # POST запрос
            async with session.post(url, data=data) as response:
                return await response.json()


# Сохранение в базу данных
async def save_to_db(message: Message, input_text, output_text):
    try:
        query = {'tg_id': message.from_user.id,
                 'td': message.date.strftime("%Y-%m-%d %H:%M:%S"),
                 'user_name': message.from_user.username,
                 'first_name': message.from_user.first_name,
                 'last_name': message.from_user.last_name,
                 'input_text': input_text,
                 'output_text': output_text}        
        return await base_request(f'{BASE_URL}/save_db', query, 'POST')
    except Exception as ex:
        await message.answer(f"save_to_db: {str(ex)}")
