from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, User
from aiogram_dialog import Dialog, DialogManager, StartMode, Window, ShowMode
from aiogram import Router
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const, Format


class StartSG(StatesGroup):
    start = State()

class SecondDialogSG(StatesGroup):
    start = State()


async def go_start(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(state=StartSG.start, mode=StartMode.RESET_STACK)

async def start_second(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(state=SecondDialogSG.start, mode=StartMode.NORMAL)

async def username_getter(dialog_manager: DialogManager, event_from_user: User, **kwargs):
    start_data_ = dialog_manager.start_data
    print(start_data_, type(start_data_))
    """{'my_data': 'my_start_data'} <class 'dict'>"""
    return {'username': event_from_user.first_name or 'Stranger',
            'start_data': [start_data_]}


start_dialog = Dialog(
    Window(
        Format('<b>Привет, {username}!</b>\n{start_data}'),
        Const('Нажми на кнопку,\nчтобы перейти во второй диалог 👇'),
        Button(Const('Кнопка'), id='go_second', on_click=start_second),
        getter=username_getter,
        state=StartSG.start),
)

second_dialog = Dialog(
    Window(
        Const('Нажми на кнопку,\nчтобы вернуться в стартовый диалог 👇'),
        Button(Const('Кнопка'), id='button_start', on_click=go_start),
        state=SecondDialogSG.start),
)

# *******************************************************************************
router_handlers = Router()
# /start
@router_handlers.message(CommandStart())
async def command_start_process(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(state=StartSG.start,
                               mode=StartMode.RESET_STACK,
                               data={'my_data': 'my_start_data'})
