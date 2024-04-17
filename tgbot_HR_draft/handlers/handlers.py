from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.types.input_file import FSInputFile
from settings import settings
from processing.chatgpt_processing import get_answer_gpt
from keyboards.keyboards import inline_first
import os


add_values = dict()
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
    received_file = message.document.file_name
    if received_file.endswith('.json'):
        if received_file not in os.listdir(RESUMES_JSON_FILES):
            await bot.download(message.document,
                               destination=f"{RESUMES_JSON_FILES}/{received_file}")
        msg1 = await message.answer(f'Резюме получено. Идет поиск подходящих вакансий...')

        global add_values
        add_values = add_values | {message.from_user.id: {'missing_skills': set(),
                                                          'pdf_files': [],
                                                          'resume_id': None}}

        answer_ = await get_answer_gpt(message, received_file)

        # -----------------------------------------------------------
        if answer_:
            # Отправка PDF отчетов админам
            for file_path in add_values[message.from_user.id]['pdf_files']:
                for user_id in settings.admin_ids:
                    await bot.send_document(user_id, FSInputFile(file_path))

        # -----------------------------------------------------------
        if answer_:
            # Приглашение пользователя ответить на вопросы
            await msg1.edit_text(answer_, reply_markup=inline_first())
