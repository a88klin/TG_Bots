from aiogram.types import Message, Voice
from aiogram import F, Bot, Router
from aiogram.filters import Command
from bot.bot_api import base_request, post_audio_ogg, save_to_db
from set.config import config  
BASE_URL = config.BASE_URL

router = Router()


@router.message(Command(commands=["start"]))
async def cmd_start(message: Message):
    await message.answer(f'Напишите вопрос или отправьте голосовое сообщение ChatGPT')


@router.message(Command(commands=["clear"]))
async def cmd_clear(message: Message):
    try:
        url = f'{BASE_URL}/clear'
        query = {"tg_id": message.from_user.id}
        method = 'GET'
        response = await base_request(url, query, method)
        await message.answer(f'The context memory has been cleared')
    except Exception as ex:
        await message.answer(f"An error occurred: {str(ex)}")


@router.message(F.text)
async def post_data(message: Message):
    try:
        query = {"text": message.text,
                 "tg_id": message.from_user.id}
        response = await base_request(f'{BASE_URL}/gpt', query, 'POST')
        if response:
            await message.answer(response)
            await save_to_db(message, message.text, response)
    except Exception as ex:
        await message.answer(f"An error occurred: {str(ex)}")


@router.message(F.voice)
async def voice_msg(message: Voice, bot: Bot):
    msg = await message.answer('Обработка голосового сообщения...')
    file_id = message.voice.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    file_content = await bot.download_file(file_path)  # Скачиваем файл
    # Сохранение аудио сообщения
    # Уникальное имя файла
    file_name = f"D:/Download/Temp/voice_{message.from_user.id}.ogg"
    with open(file_name, 'wb') as f:
        f.write(file_content.read())  # Сохраняем файл
    response = await post_audio_ogg(f'{BASE_URL}/upload-audio', message)
    if response:
        await msg.edit_text(f"Ваше аудио сообщение: {response['text_message']} \n\n{response['answer']}")
        await save_to_db(message, response['text_message'], response['answer'])
