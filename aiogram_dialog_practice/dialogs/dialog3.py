from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, User
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.text import Const, Format, Case, List, Multi
from aiogram_dialog.widgets.kbd import (Select, Checkbox, ManagedCheckbox,
                                        Column, Multiselect)
from aiogram import Router, F, Bot
import operator


class StartSG(StatesGroup):
    start = State()

# ----------------------------------------------------------------------------
# Это хэндлер, срабатывающий на нажатие кнопки с категорией товаров
async def category_selection(callback: CallbackQuery, widget: Select,
                             dialog_manager: DialogManager, item_id: str):
    await callback.message.edit_text(f'Выбрана категория с id={item_id}.')
    await dialog_manager.done()

# Хэндлер, обрабатывающий нажатие кнопки в виджете `Checkbox`
async def checkbox_clicked(callback: CallbackQuery, checkbox: ManagedCheckbox,
                           dialog_manager: DialogManager):
    dialog_manager.dialog_data.update(is_checked=checkbox.is_checked())


# геттер
async def get_categories(**kwargs):
    categories = [
        ('Техника', 7),
        ('Одежда', 8),
        ('Обувь', 9),
    ]
    return {'categories': categories}

# Геттер
async def getter(dialog_manager: DialogManager, **kwargs):
    checked = dialog_manager.dialog_data.get('is_checked')
    return {'checked': checked,
            'not_checked': not checked}

# Геттер
async def get_topics(dialog_manager: DialogManager, **kwargs):
    topics = [
        ("IT", '1'),
        ("Дизайн", '2'),
        ("Наука", '3'),
        ("Общество", '4'),
        ("Культура", '5'),
        ("Искусство", '6'),
    ]
    return {"topics": topics}


# ------------------------------------------------------------
start_dialog = Dialog(
    Window(
        Const(text='Выберите категорию:'),

        Select(
            Format('{item[0]}'),
            id='categ',
            # item_id_getter=lambda x: x[1],
            item_id_getter=operator.itemgetter(1),
            items='categories',
            on_click=category_selection
        ),

        Const(text='Демонстрация работы виджета <code>Checkbox</code>\n'),
        Const(text='Сейчас дополнительного текста нет', when='not_checked'),
        Const(text='Дополнительный текст есть:\n<b>Это дополнительный текст</b>', when='checked'),
        Checkbox(
            checked_text=Const('[✔️] Отключить'),
            unchecked_text=Const('[ ] Включить'),
            id='checkbox',
            default=False,
            on_state_changed=checkbox_clicked,
        ),

        Const(text='Отметьте темы новостей 👇'),
        Column(
            Multiselect(
                checked_text=Format('[✔️] {item[0]}'),
                unchecked_text=Format('[  ] {item[0]}'),
                id='multi_topics',
                item_id_getter=operator.itemgetter(1),
                items="topics",),
        ),

        state=StartSG.start,
        getter=[get_categories, getter, get_topics]
    ),
)

# *******************************************************************************
router_handlers = Router()
# /start
@router_handlers.message(CommandStart())
async def command_start_process(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(state=StartSG.start, mode=StartMode.RESET_STACK)
