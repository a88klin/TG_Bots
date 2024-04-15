from aiogram import Router, F, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode
from lang_models.parser import to_dict_parser, Resume
from handlers.dialog import Check, set_data
from config import settings


router = Router()

# На команду или меню "/start" от пользователя
@router.message(CommandStart(), F.from_user.id.not_in(settings.ADMIN_IDS))
async def start_command(message: Message):
    await message.answer('Здравствуйте! Вышлите информацию о себе, в т.ч. '
                         'полное имя, желаемую позицию, владение навыками и технологиями')


# На текстовое сообщение от пользователя
@router.message(F.text, F.text != '/start')
async def start_work(message: Message, bot: Bot, dialog_manager: DialogManager):
    await message.answer('Ваша информация обрабатывается...')
    dict_info = await to_dict_parser(message.text, Resume) # Ответ от Парсера

    # Диалог по проверке информации у пользователя
    await dialog_manager.start(state=Check.initial, mode=StartMode.RESET_STACK)
    await set_data(dialog_manager, dict_info)
    dialog_manager.dialog_data['all_message'] = message.text
    dialog_manager.dialog_data['user_id'] = message.from_user.id

    # Сообщение админам
    for _id in settings.ADMIN_IDS:
        await bot.send_message(chat_id=_id,
              text=f'Информация от пользователя: {message.from_user.username} '
                   f'(id: {message.from_user.id})')
