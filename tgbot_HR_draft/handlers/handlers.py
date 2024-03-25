from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message
from settings import settings
from processing.resume_processing import get_answer_gpt
import os


RESUMES_JSON_FILES = settings.resumes_json_files
router = Router()

# Хэндлер на команду "/start"
@router.message(Command(commands=["start"]))
async def process_start_command(message: Message):
    await message.answer('Здравствуйте! Загрузите резюме в фомате JSON')


# Хэндлер на отправленный Json файл резюме
@router.message(F.document)
async def download_json(message: Message, bot: Bot):
    received_file = message.document.file_name
    if received_file.endswith('.json'):
        if received_file not in os.listdir(RESUMES_JSON_FILES):
            await bot.download(message.document,
                               destination=f"{RESUMES_JSON_FILES}/{received_file}")
        await message.answer('Резюме получено. Идет поиск подходящих вакансий...')
        answer_ = await get_answer_gpt(received_file)
        # print(answer_)
        await message.answer(answer_)
