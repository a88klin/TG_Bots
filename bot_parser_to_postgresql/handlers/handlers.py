from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message
from dbase.database import add_user_and_massage
from lang_models.parser import to_dict_parser
from config import settings


router = Router()

# На команду или меню "/start" от пользователя
@router.message(Command(commands=["start"]), F.from_user.id.not_in(settings.ADMIN_IDS))
async def start_command(message: Message):
    await message.answer('Здравствуйте! Вышлите о себе эссе в свободной форме '
                         'в одном сообщении. В т.ч. укажите свое ФИО, дату рождения, '
                         'образование, предыдущие места работы и должности.')


# На текстовое сообщение от пользователя
@router.message(F.text, F.text != '/start')
async def answer(message: Message, bot: Bot):

    dict_info = await to_dict_parser(message.text)
    # запись в базу данных
    await add_user_and_massage(message.from_user.id, dict_info, message.text)

    # Сообщение пользователю
    await message.answer('Спасибо! Ваше эссе получено.')

    # Сообщение админам
    for _id in settings.ADMIN_IDS:
        await bot.send_message(
            chat_id=_id,
            text=f'Сообщение от пользователя (id: {message.from_user.id}): {dict_info}')
