from aiogram import Router, F, types, Bot
from aiogram.filters import Command
from keyboards.buttons import main_keyboard, main_keyboard2, inline_keyboard, inline_keyboard2
from utils.my_libs import ask_gpt, n10, stt_free
from random import randint
from config_set import config

allowed_ids = config.allowed_ids


async def voice_msg(message: types.Voice, bot: Bot):
    msg = await message.answer('Обработка голосового сообщения...')
    file_id = message.voice.file_id
    # await bot.download(message.voice, destination='file.ogg')
    file_info = await bot.get_file(file_id=file_id)
    file = await bot.download_file(file_info.file_path)  # _io.BytesIO object

    ask_text = stt_free(file)
    if ask_text:
        await msg.edit_text(f'Ваш вопрос: {ask_text}')

    msg2 = await message.answer('Формирование ответа ChatGPT...')
    answer_gpt = await ask_gpt(ask_text, model='GPT35')
    if answer_gpt:
        await msg2.edit_text(answer_gpt)


async def cmd_start(message: types.Message):
    await message.answer("Hello!", reply_markup=main_keyboard())
async def cmd_start2(message: types.Message):
    await message.answer("Hello!", reply_markup=main_keyboard2())
async def in_board(message: types.Message):
    await message.answer(r"/inline", reply_markup=inline_keyboard())
async def in_board2(message: types.Message):
    await message.answer(r"/inline2", reply_markup=inline_keyboard2())

async def gpt(message: types.Message):
    answer_gpt = await ask_gpt(message.text, model='GPT35')
    await message.answer(answer_gpt)

async def get_n10(message: types.Message):
    await message.answer(str(n10(message.text)))
async def get_random(message: types.Message):
    await message.answer(f"{randint(0, 100)} - {randint(0, 100)}")
async def get_random2(callback: types.CallbackQuery):
    await callback.message.answer(f"{randint(0, 100)} - {randint(0, 100)}")
async def send_photo(message: types.Message):
    photo = 'https://electricauto.by/image/catalog/photo_2023-02-03_11-03-21.jpg'
    await message.answer_photo(photo=photo)


router = Router()

def register_other(router):
    router.message.register(voice_msg, F.from_user.id.in_(allowed_ids), F.voice)

    router.message.register(gpt, F.from_user.id.in_(allowed_ids),
                                 F.text.regexp('\w+(\s\w+)+'))  # более одного слова

    router.message.register(cmd_start, F.from_user.id.in_(allowed_ids), Command("start"))
    router.message.register(cmd_start2, F.from_user.id.in_(allowed_ids), Command("start2"))
    router.message.register(in_board, F.from_user.id.in_(allowed_ids), Command("inline"))
    router.message.register(in_board2, F.from_user.id.in_(allowed_ids), Command("inline2"))

    router.message.register(get_n10, F.from_user.id.in_(allowed_ids),
                                     F.text.regexp(r'^\d+$')) # Numbers only

    router.message.register(get_random, F.from_user.id.in_(allowed_ids),
                                        F.text.lower() == 'random')
    router.callback_query.register(get_random2, F.from_user.id.in_(allowed_ids),
                                                F.data == 'random')

    router.message.register(send_photo, F.from_user.id.in_(allowed_ids),
                                        F.text.lower()=='zeekr', # AND (the same)
                                        F.text.regexp('(?i)zeekr')) # в нижний регистр
