from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, User
from aiogram_dialog import Dialog, DialogManager, StartMode, Window, ShowMode
from aiogram import Router
from aiogram.enums import ContentType, ParseMode
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput, MessageInput
from aiogram_dialog.widgets.text import Const


class StartSG(StatesGroup):
    start = State()

# ----------------------------------------------------------------------------
# Проверка текста на то, что он содержит число от 3 до 120 включительно
def age_check(text: ContentType.TEXT) -> str:
    if all(ch.isdigit() for ch in text) and 3 <= int(text) <= 120:
        return text
    raise ValueError


# Хэндлер, который сработает, если пользователь ввел корректный возраст
async def correct_age_handler(
        message: Message,
        widget: ManagedTextInput,
        dialog_manager: DialogManager,
        text: str) -> None:
    dialog_manager.show_mode = ShowMode.NO_UPDATE
    await message.answer(text=f'Вам {text}')


# Хэндлер, который сработает на ввод некорректного возраста
async def error_age_handler(
        message: Message,
        widget: ManagedTextInput,
        dialog_manager: DialogManager,
        error: ValueError):
    await message.answer(
        text='Вы ввели некорректный возраст. Попробуйте еще раз'
    )

# Хэндлер, который сработает, если пользователь отправил вообще не текст
async def no_text(message: Message, widget: MessageInput, dialog_manager: DialogManager):
    print(type(widget))
    await message.answer(text='Вы ввели вообще не текст!')


start_dialog = Dialog(
    Window(
        Const(text='Введите ваш возраст'),
        TextInput(
            id='age_input',
            type_factory=age_check,
            on_success=correct_age_handler,
            on_error=error_age_handler,
        ),
        MessageInput(
            func=no_text,
            content_types=ContentType.ANY
        ),
        state=StartSG.start,
    ),
)

"""Сначала идет ожидание текста. Если текст корректный - срабатывает один хэндлер. 
Если текст некорректный - другой. А если вообще не текст - апдейт не попадет в виджет TextInput, 
а попадает в виджет MessageInput, где тоже можно настроить реакцию бота."""

# *******************************************************************************
router_handlers = Router()
# /start
@router_handlers.message(CommandStart())
async def command_start_process(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(state=StartSG.start, mode=StartMode.RESET_STACK)
