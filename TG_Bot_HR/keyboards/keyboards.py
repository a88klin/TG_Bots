from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


def inline_mode():
    builder = InlineKeyboardBuilder()
    builder.button(text="Подбор вакансий", callback_data='selection')
    builder.button(text="Анализ Резюме vs Вакансия", callback_data='analysis')
    builder.adjust(1)
    return builder.as_markup()


def digit_kb_reply():
    items = ['0', '1', '2', '3', '4', '5', '6', '7']
    builder = ReplyKeyboardBuilder()
    [builder.button(text=item) for item in items]
    builder.adjust(8)
    return builder.as_markup(resize_keyboard=True,
                             one_time_keyboard=True,
                             input_field_placeholder='Или напиши ответ здесь')


def digit_kb_inline():
    items = ['0', '1', '2', '3', '4', '5', '6', '7']
    builder = InlineKeyboardBuilder()
    [builder.button(text=item, callback_data=item) for item in items]
    builder.adjust(8)
    return builder.as_markup()


def inline_first():
    builder = InlineKeyboardBuilder()
    builder.button(text="Завершить", callback_data='_exit')
    builder.button(text="Согласен", callback_data='_yes')
    builder.adjust(2)
    return builder.as_markup()
