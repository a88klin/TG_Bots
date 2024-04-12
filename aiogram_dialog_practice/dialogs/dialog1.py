from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, User
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import Button, Row
from aiogram import Router, F, Bot


class StartSG(StatesGroup):
    start = State()


# Хэндлер, обрабатывающий нажатие на кнопку 'Да'
async def yes_click_process(callback: CallbackQuery,
                            widget: Button,
                            dialog_manager: DialogManager):
    await callback.message.edit_text(
        text='<b>Прекрасно!</b>\nНадеюсь, вы найдете в этом курсе что-то '
             'новое и полезное для себя!'
    )
    await dialog_manager.done()


# Хэндлер, обрабатывающий нажатие на кнопку 'Нет'
async def no_click_process(callback: CallbackQuery,
                           widget: Button,
                           dialog_manager: DialogManager):
    await callback.message.edit_text(
        text='<b>Попробуйте!</b>\nСкорее всего, вам понравится!'
    )
    await dialog_manager.done()


# Getter
async def get_username(event_from_user: User, **kwargs):
    return {'username': event_from_user.username}


start_dialog = Dialog(
    Window(
        Format(text='Привет, <b>{username}</b>!'),
        Const(text='Пробовали ли вы уже писать ботов с использованием '
                   'библиотеки <code>aiogram_dialog</code>?'),
        Row(Button(text=Const('✅ Да'), id='yes', on_click=yes_click_process),
            Button(text=Const('✖️ Нет'), id='no', on_click=no_click_process),
        ),
        getter=get_username,
        state=StartSG.start,
    ),
)

# *******************************************************************************
router_handlers = Router()
# /start
@router_handlers.message(CommandStart())
async def command_start_process(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(state=StartSG.start, mode=StartMode.RESET_STACK)
