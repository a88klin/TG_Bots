from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, User
from aiogram_dialog import Dialog, DialogManager, StartMode, Window, ShowMode
from aiogram import Router
from aiogram_dialog.widgets.kbd import Button, Row, Start, Cancel, Next, Back, SwitchTo
from aiogram_dialog.widgets.text import Const


class StartSG(StatesGroup):
    first = State()
    second = State()
    third = State()

class SecondDialogSG(StatesGroup):
    first = State()
    second = State()

# ******************************************
async def close_second_dialog(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager):
    print('close_second_dialog')


async def go_second_dialog(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager):
    print(SecondDialogSG.first)


async def first_one(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager):
    print(StartSG.first)


async def first_two(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager):
    print(StartSG.second)


async def first_three(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager):
    print(StartSG.third)


async def second_one(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager):
    print(SecondDialogSG.first)


async def second_two(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager):
    print(SecondDialogSG.second)

# **********************************************************************
start_dialog = Dialog(
    Window(
        Const('<b>Вы находитесь в 1 (первом) окне 1-го диалога</b>\n'),
        Const('Вы можете переключаться между окнами текущего диалога, '
              'или перейти в новый 👇'),
        Row(
            SwitchTo(Const('2️⃣'), id='first_second', state=StartSG.second, on_click=first_two),
            SwitchTo(Const('3️⃣'), id='first_third', state=StartSG.third, on_click=first_three)
        ),
        Row(
            Back(Const('◀️  Назад'), id='first_back', on_click=first_three),
            Next(Const('Вперед ▶'), id='first_next', on_click=first_two),
        ),
        Start(Const('Во 2-й диалог ▶️'), id='go_second_dialog',
                     state=SecondDialogSG.first, on_click=go_second_dialog),
        state=StartSG.first
    ),

    Window(
        Const('<b>Вы находитесь во 2 (втором) окне 1-го диалога</b>\n'),
        Const('Вы можете переключаться между окнами текущего диалога, '
              'или перейти в новый 👇'),
        Row(
            SwitchTo(Const('1️⃣'), id='first_first', state=StartSG.first, on_click=first_one),
            SwitchTo(Const('3️⃣'), id='first_third', state=StartSG.third, on_click=first_three),
        ),
        Row(
            Back(Const('◀️  Назад'), id='first_back', on_click=first_one),
            Next(Const('Вперед ▶'), id='first_next', on_click=first_three),
        ),
        Start(Const('Во 2-й диалог ▶️'), id='go_second_dialog',
                     state=SecondDialogSG.first, on_click=go_second_dialog),
        state=StartSG.second
    ),

    Window(
        Const('<b>Вы находитесь в 3 (третьем) окне 1-го диалога</b>\n'),
        Const('Вы можете переключаться между окнами текущего диалога, '
              'или перейти в новый 👇'),
        Row(
            SwitchTo(Const('1️⃣'), id='first_first', state=StartSG.first, on_click=first_one),
            SwitchTo(Const('2️⃣'), id='first_second', state=StartSG.second, on_click=first_two),
        ),
        Back(Const('◀️  Назад'), id='first_back', on_click=first_two),
        Start(Const('Во 2-й диалог ▶️'), id='go_second_dialog',
                     state=SecondDialogSG.first, on_click=go_second_dialog),
        state=StartSG.third
    ),
)


second_dialog = Dialog(
    Window(
        Const('<b>Вы находитесь в 1 (первом) окне 2-го диалога!</b>\n'),
        Const('Нажмите на кнопку Отмена,\nчтобы вернуться в стартовый диалог 👇'),
        SwitchTo(Const('2️⃣'), id='second_second', state=SecondDialogSG.second, on_click=second_two),
        Row(
            Back(Const('◀️  Назад'), id='second_back', on_click=second_two),
            Next(Const('Вперед ▶'), id='second_next', on_click=second_two),
        ),
        Cancel(Const('Отмена'), id='button_cancel', on_click=close_second_dialog),
        state=SecondDialogSG.first
    ),

    Window(
        Const('<b>Вы находитесь во 2 (втором) окне 2-го диалога!</b>\n'),
        Const('Нажмите на кнопку Отмена,\nчтобы вернуться в стартовый диалог 👇'),
        SwitchTo(Const('1️⃣'), id='second_first', state=SecondDialogSG.first, on_click=second_one),
        Back(Const('◀️  Назад'), id='second_back', on_click=second_one),
        Cancel(Const('Отмена'), id='button_cancel', on_click=close_second_dialog),
        state=SecondDialogSG.second
    ),
)

# *******************************************************************************
router_handlers = Router()
# /start
@router_handlers.message(CommandStart())
async def command_start_process(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(state=StartSG.first,
                               mode=StartMode.RESET_STACK)
