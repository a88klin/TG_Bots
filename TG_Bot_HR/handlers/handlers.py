from aiogram import Router, F, Bot, types
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.types.input_file import FSInputFile
from settings import settings
from processing.chatgpt_processing import get_answer_gpt
from processing.resume_vs_vacancy import main_vs
from keyboards.keyboards import inline_first, inline_mode
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
import os


add_values = dict()
RESUMES_JSON_FILES = settings.resumes_json_files
router = Router()

class Mode(StatesGroup):
    mode = State()

@router.message(Command(commands=["start"]))
async def process_start_command(message: Message):
    await message.answer('Здравствуйте! Выберите режим:', reply_markup=inline_mode())

@router.callback_query(F.data=='selection')
async def process_start_command(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(Mode.mode)
    await state.update_data(mode=callback.data)
    await callback.message.delete()
    await callback.message.answer('Загрузите резюме в фомате JSON для поиска вакансий. '
                                  'После обработки резюме вам будет предложено ответить на вопросы')

@router.callback_query(F.data=='analysis')
async def process_start_command(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(Mode.mode)
    await state.update_data(mode=callback.data)
    await callback.message.delete()
    await callback.message.answer('Загрузите резюме в фомате JSON для сравнения.')


# Хэндлер на отправленный Json файл резюме
@router.message(F.document)
async def download_resume_json(message: Message, bot: Bot, state: FSMContext):
    global add_values
    received_file = message.document.file_name
    if received_file.endswith('.json'):
        data = await state.get_data()

        # JSON резюме для поиска вакансий ****************************************************
        if data.get('mode') == 'selection':
            await state.clear()
            if received_file not in os.listdir(RESUMES_JSON_FILES):
                await bot.download(message.document,
                                   destination=f"{RESUMES_JSON_FILES}/{received_file}")
            msg1 = await message.answer('Резюме получено. Идет поиск подходящих вакансий...')

            add_values = add_values | {message.from_user.id: {'missing_skills': set(),
                                                              'pdf_files': [],
                                                              'resume_id': None}}
            answer_ = await get_answer_gpt(message, received_file)
            # -----------------------------------------------------------
            if answer_:
                for file_path in add_values[message.from_user.id]['pdf_files']:
                    await bot.send_document(message.from_user.id, FSInputFile(file_path)) # Отправка PDF отчета пользователю
                    try:
                        for user_id in settings.admin_ids:
                            await bot.send_document(user_id, FSInputFile(file_path)) # Отправка PDF отчетов админам
                    except Exception as ex:
                        print('Error: Отправка PDF отчетов админам', '\n', ex)
            # -----------------------------------------------------------
            if answer_:
                await msg1.edit_text(answer_)
                await message.answer('Ответьте пожалуйста на уточняющие вопросы',
                                     reply_markup=inline_first())

        # JSON резюме для сравнения с вакансией *********************************************
        elif data.get('mode') == 'analysis':
            os.makedirs('data/vs', exist_ok=True)
            await bot.download(message.document, destination=f"data/vs/{received_file}")
            add_values = {message.from_user.id: {'resume_file': f"data/vs/{received_file}"}}
            await state.set_state(Mode.mode)
            await state.update_data(mode='get_vacancy')
            await message.answer('Резюме получено. Загрузите вакансию в формате JSON')

        else: # сюда попадет вакансия
            data = await state.get_data()
            await state.clear()
            if data.get('mode') == 'get_vacancy':
                await bot.download(message.document, destination=f"data/vs/{received_file}")
                vacancy_file = f"data/vs/{received_file}"
                msg = await message.answer('Вакансия получена. Идет анализ вакансии и резюме...')
                pdf_path = await main_vs(add_values[message.from_user.id]['resume_file'], vacancy_file)
                del add_values[message.from_user.id]

                if pdf_path:
                    await bot.send_document(message.from_user.id, FSInputFile(pdf_path))
                    try:
                        for user_id in settings.admin_ids:
                            await bot.send_document(user_id, FSInputFile(pdf_path))
                        await msg.edit_text('Сравнительный анализ выполнен. Начните сначала через меню /start')
                    except Exception as ex:
                        print('Error: Отправка PDF отчетов админам', '\n', ex)
