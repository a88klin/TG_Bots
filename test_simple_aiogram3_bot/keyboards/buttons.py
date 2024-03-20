from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


def main_keyboard():
    kb = [
          [ types.KeyboardButton(text="Coin"),
            types.KeyboardButton(text="Moon"),
            types.KeyboardButton(text="Minsk") ],
          [ types.KeyboardButton(text="Random") ],
          ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Введите команду")
    return keyboard


def main_keyboard2():
    builder = ReplyKeyboardBuilder()
    builder.button(text="Coin")
    builder.button(text="Moon")
    builder.button(text="Minsk")
    builder.button(text="Random")
    builder.adjust(3, 1)
    return builder.as_markup(resize_keyboard=True,
                             input_field_placeholder="Введите команду")


def inline_keyboard():
    kb = [
        [types.InlineKeyboardButton(text="Coin", callback_data='coin'),
         types.InlineKeyboardButton(text="Moon", callback_data='moon'),
         types.InlineKeyboardButton(text="Minsk", callback_data='minsk')],
        [types.InlineKeyboardButton(text="Random 100", callback_data='random')],
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)
    return keyboard


def inline_keyboard2():
    builder = InlineKeyboardBuilder()
    builder.button(text="Coin", callback_data='coin')
    builder.button(text="Moon", callback_data='moon')
    builder.button(text="Minsk", callback_data='minsk')
    builder.button(text="Random 100", callback_data='random')
    builder.button(text="в этом же чате", switch_inline_query_current_chat='')
    builder.button(text="query=", switch_inline_query='')
    builder.adjust(3, 3)
    return builder.as_markup()
