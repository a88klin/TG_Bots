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
# Хэндлер, который сработает на любой апдейт типа `Message`
# за исключением команды /start
async def message_handler(
        message: Message,
        widget: MessageInput,
        dialog_manager: DialogManager) -> None:
    dialog_manager.show_mode = ShowMode.NO_UPDATE
    await message.send_copy(message.chat.id)


start_dialog = Dialog(
    Window(
        Const(text='Пришлите мне что-нибудь и я отправлю вам копию обратно'),
        MessageInput(
            func=message_handler,
            content_types=ContentType.ANY,
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
