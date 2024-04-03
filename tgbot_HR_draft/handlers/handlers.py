from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message
from settings import settings
from processing.chatgpt_processing import get_answer_gpt
from keyboards.keyboards import inline_first
import os


RESUMES_JSON_FILES = settings.resumes_json_files
router = Router()

# Хэндлер на команду "/start"
@router.message(Command(commands=["start"]))
async def process_start_command(message: Message):
    await message.answer('Здравствуйте! Загрузите резюме в фомате JSON. '
                         'После обработки резюме вам будет предложено ответить на вопросы')


# Хэндлер на отправленный Json файл резюме
@router.message(F.document)
async def download_json(message: Message, bot: Bot):
    global resume_id
    received_file = message.document.file_name
    if received_file.endswith('.json'):
        if received_file not in os.listdir(RESUMES_JSON_FILES):
            await bot.download(message.document,
                               destination=f"{RESUMES_JSON_FILES}/{received_file}")
        msg1 = await message.answer(f'Резюме получено. Идет поиск подходящих вакансий...')
        answer_ = await get_answer_gpt(received_file)
        if answer_:
            await msg1.edit_text(answer_, reply_markup=inline_first())
