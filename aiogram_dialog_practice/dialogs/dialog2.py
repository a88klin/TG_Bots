from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, User
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.text import Const, Format, Case, List, Multi
from aiogram_dialog.widgets.kbd import Button, Row, Column, Group
from aiogram import Router, F, Bot
import random


class StartSG(StatesGroup):
    start = State()

# ----------------------------------------------------------------------------
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

# -------------------------------------------------------------------------
async def get_number(**kwargs):
    return {'number': random.randint(1, 3)}

async def get_items(**kwargs):
    return {'items': (
        (1, 'Пункт 1'),
        (2, 'Пункт 2'),
        (3, 'Пункт 3'),
    )}

async def get_username(event_from_user: User, **kwargs):
    return {'username': event_from_user.username}


# Несколько виджетов в одном окне -----------------------------------------
start_dialog = Dialog(
    Window(
        Case(texts={
                1: Const('Case randint 1'),
                2: Const('Case randint 2'),
                3: Const('Case randint 3'),},
        selector='number',),

        Multi(
            List(field=Format('<b>{item[0]}</b>. {item[1]}'), items='items'),
            Format(text='\nПривет, <b>{username}</b>!'),
            Const(text='Пробовали ли вы уже писать ботов с использованием '
                       'библиотеки <code>aiogram_dialog</code>?'),
            sep='\n',),

        Group(Button(text=Const('1'), id='button_1'),
            Button(text=Const('2'), id='button_2'),
            Button(text=Const('3'), id='button_3'),
            Button(text=Const('4'), id='button_4'),
            Button(text=Const('5'), id='button_5'),
            Button(text=Const('6'), id='button_6'),
            Button(text=Const('7'), id='button_7'),
            Button(text=Const('8'), id='button_8'), width=8),

        Group(
            Column(
                    Button(text=Const('✅ Да'), id='yes', on_click=yes_click_process),
                    Button(text=Const('✖️ Нет'), id='no', on_click=no_click_process),),
            Row(
                Button(text=Const('✅ Да'), id='yes', on_click=yes_click_process),
                Button(text=Const('✖️ Нет'), id='no', on_click=no_click_process),),
            # width=3,
        ),

        getter=[get_number, get_items, get_username],
        state=StartSG.start,
    ),
)

# *******************************************************************************
router_handlers = Router()
# /start
@router_handlers.message(CommandStart())
async def command_start_process(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(state=StartSG.start, mode=StartMode.RESET_STACK)
