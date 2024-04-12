from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, User
from aiogram_dialog import Dialog, DialogManager, StartMode, Window, ShowMode
from aiogram import Router
from aiogram_dialog.widgets.kbd import Button, Row
from aiogram_dialog.widgets.text import Const


class StartSG(StatesGroup):
    first = State()
    second = State()
    third = State()


class SecondDialogSG(StatesGroup):
    first = State()
    second = State()


async def close_second_dialog(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager):
    await dialog_manager.done()


async def go_second_dialog(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager):
    await dialog_manager.start(state=SecondDialogSG.first)


async def switch_to_first_one(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager):
    await dialog_manager.switch_to(state=StartSG.first)


async def switch_to_first_two(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager):
    await dialog_manager.switch_to(state=StartSG.second)


async def switch_to_first_three(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager):
    await dialog_manager.switch_to(state=StartSG.third)


async def switch_to_second_one(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager):
    await dialog_manager.switch_to(state=SecondDialogSG.first)


async def switch_to_second_two(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager):
    await dialog_manager.switch_to(state=SecondDialogSG.second)


start_dialog = Dialog(
    Window(
        Const('<b>Вы находитесь в первом окне первого диалога</b>\n'),
        Const('Вы можете переключаться между окнами текущего диалога, '
              'или перейти в новый 👇'),
        Row(
            Button(Const('2️⃣'), id='w_second', on_click=switch_to_first_two),
            Button(Const('3️⃣'), id='w_third', on_click=switch_to_first_three),
        ),
        Button(Const('Во 2-й диалог ▶️'), id='go_second_dialog', on_click=go_second_dialog),
        state=StartSG.first
    ),

    Window(
        Const('<b>Вы находитесь во втором окне первого диалога</b>\n'),
        Const('Вы можете переключаться между окнами текущего диалога, '
              'или перейти в новый 👇'),
        Row(
            Button(Const('1️⃣'), id='w_first', on_click=switch_to_first_one),
            Button(Const('3️⃣'), id='w_third', on_click=switch_to_first_three),
        ),
        Button(Const('Во 2-й диалог ▶️'), id='go_second_dialog', on_click=go_second_dialog),
        state=StartSG.second
    ),

    Window(
        Const('<b>Вы находитесь в третьем окне первого диалога</b>\n'),
        Const('Вы можете переключаться между окнами текущего диалога, '
              'или перейти в новый 👇'),
        Row(
            Button(Const('1️⃣'), id='w_first', on_click=switch_to_first_one),
            Button(Const('2️⃣'), id='w_second', on_click=switch_to_first_two),
        ),
        Button(Const('Во 2-й диалог ▶️'), id='go_second_dialog', on_click=go_second_dialog),
        state=StartSG.third
    ),
)


second_dialog = Dialog(
    Window(
        Const('<b>Вы находитесь в первом окне второго диалога!</b>\n'),
        Const('Нажмите на кнопку Отмена,\nчтобы вернуться в стартовый диалог 👇'),
        Button(Const('2️⃣'), id='w_second', on_click=switch_to_second_two),
        Button(Const('Отмена'), id='button_cancel', on_click=close_second_dialog),
        state=SecondDialogSG.first
    ),

    Window(
        Const('<b>Вы находитесь во втором окне второго диалога!</b>\n'),
        Const('Нажмите на кнопку Отмена,\nчтобы вернуться в стартовый диалог 👇'),
        Button(Const('1️⃣'), id='w_first', on_click=switch_to_second_one),
        Button(Const('Отмена'), id='button_cancel', on_click=close_second_dialog),
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
