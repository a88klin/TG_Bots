from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, User
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput
from aiogram_dialog.widgets.text import Const, Format, Case, List, Multi
from aiogram import Router, F, Bot


class StartSG(StatesGroup):
    start = State()

# ----------------------------------------------------------------------------
# Проверка текста на то, что он содержит число от 3 до 120 включительно
def age_check(text: str) -> str:
    print(text)
    if all(ch.isdigit() for ch in text) and 3 <= int(text) <= 120:
        return text
    raise ValueError

# Хэндлер, который сработает, если пользователь ввел корректный возраст
async def correct_age_handler(
        message: Message,
        widget: ManagedTextInput,
        dialog_manager: DialogManager,
        text: str) -> None:
    await message.answer(text=f'Вам {text}')
    await dialog_manager.done()

# Хэндлер, который сработает на ввод некорректного возраста
async def error_age_handler(
        message: Message,
        widget: ManagedTextInput,
        dialog_manager: DialogManager,
        error: ValueError):
    await message.answer(
        text='Вы ввели некорректный возраст. Попробуйте еще раз')

# ------------------------------------------------------------
start_dialog = Dialog(
    Window(
        Const(text='Введите ваш возраст'),
        TextInput(
            id='age_input',
            type_factory=age_check,
            on_success=correct_age_handler,
            on_error=error_age_handler,
        ),
        state=StartSG.start,
    ),
)

# *******************************************************************************
router_handlers = Router()
# /start
@router_handlers.message(CommandStart())
async def command_start_process(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(state=StartSG.start, mode=StartMode.RESET_STACK)
