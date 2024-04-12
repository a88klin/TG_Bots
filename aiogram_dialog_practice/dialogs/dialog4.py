from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, User
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.text import Const, Format, Case, List, Multi
from aiogram_dialog.widgets.kbd import (Select, Checkbox, Radio,
                                        Column, Multiselect)
from aiogram import Router, F, Bot
import operator


class StartSG(StatesGroup):
    start = State()

# ----------------------------------------------------------------------------
async def lang_selection(callback: CallbackQuery, widget: Radio,
                         dialog_manager: DialogManager, item_id: str):
    print(f'Выбран язык с id={item_id}. {type(item_id)}. {callback.data}. {type(callback.data)}')
    """Выбран язык с id=1. <class 'str'>. radio_lang_id:1. <class 'str'>"""
    # await callback.message.edit_text(f'id={item_id}. {callback.data}')
    # await dialog_manager.done()


# Геттер
async def get_languages(dialog_manager: DialogManager, **kwargs):
    checked = dialog_manager.find('radio_lang').get_checked()
    language = {
        '1': 'en',
        '2': 'ru',
        '3': 'fr'
    }
    chosen_lang = language['2' if not checked else checked]
    lang = {
        'ru': {
            '1': '🇬🇧 Английский',
            '2': '🇷🇺 Русский',
            '3': '🇫🇷 Французский',
            'text': 'Выберите язык'
        },
        'en': {
            '1': '🇬🇧 English',
            '2': '🇷🇺 Russian',
            '3': '🇫🇷 French',
            'text': 'Choose language'
        },
        'fr': {
            '1': '🇬🇧 Anglais',
            '2': '🇷🇺 Russe',
            '3': '🇫🇷 Français',
            'text': 'Choisissez la langue'
        }
    }
    languages = [
        (f"{lang[chosen_lang]['1']}", '1'),
        (f"{lang[chosen_lang]['2']}", '2'),
        (f"{lang[chosen_lang]['3']}", '3'),
    ]
    return {"languages": languages,
            'text': lang[chosen_lang]['text']}


# ------------------------------------------------------------
start_dialog = Dialog(
    Window(
        Format(text='{text}'),
        Column(
            Radio(
                checked_text=Format('🔘 {item[0]}'),
                unchecked_text=Format('⚪️ {item[0]}'),
                id='radio_lang_id',
                item_id_getter=operator.itemgetter(1),
                items="languages",
                on_click=lang_selection,
                # on_state_changed=None,
            ),
        ),
        state=StartSG.start,
        getter=get_languages),
    )

# *******************************************************************************
router_handlers = Router()
# /start
@router_handlers.message(CommandStart())
async def command_start_process(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(state=StartSG.start, mode=StartMode.RESET_STACK)
