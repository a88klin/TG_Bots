from aiogram.types import Message, Voice
from aiogram import F, Bot, Router
from aiogram.filters import Command
from aiogram.types import BotCommand
from assistant import get_answer, clear_memory
from libs import stt
from set.config import config


allowed_ids = config.ALLOWED_IDS
router = Router()


@router.startup()
async def set_menu_botton(bot: Bot):
    main_menu_commands = [
        BotCommand(command='/start', description='Start'),
        BotCommand(command='/clear', description='Clear context memory')]
    await bot.set_my_commands(main_menu_commands)


@router.message(Command(commands=["start"]))
async def cmd_start(message: Message):
    await message.answer(f'Напишите запрос или отправьте голосовое сообщение')


@router.message(Command(commands=["clear"]))
async def cmd_clear(message: Message):
    try:
        response = await clear_memory(message.from_user.id)
        await message.answer(response)
    except Exception as ex:
        await message.answer(f"Error: {str(ex)}")


@router.message(F.from_user.id.in_(allowed_ids), F.text)
async def text_msg(message: Message):
    msg = await message.answer('Обработка сообщения...')
    try:
        answer_gpt = await get_answer(message.text, message.from_user.id)
        await msg.edit_text(answer_gpt)
    except Exception as ex:
        await msg.edit_text(f"Error: {str(ex)}")


@router.message(F.from_user.id.in_(allowed_ids), F.voice)
async def voice_msg(message: Voice, bot: Bot):
    msg = await message.answer('Обработка голосового сообщения...')
    file_id = message.voice.file_id
    # await bot.download(message.voice, destination='file.ogg')
    file_info = await bot.get_file(file_id=file_id)
    file = await bot.download_file(file_info.file_path)  # _io.BytesIO object
    text_from_voice = await stt(file)
    await msg.edit_text(f'Ваш вопрос: {text_from_voice}')
    # ----------
    msg2 = await message.answer('Формирование ответа...')
    answer_gpt = await get_answer(text_from_voice, message.from_user.id)
    await msg2.edit_text(answer_gpt)
