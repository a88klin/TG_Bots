from voice_gpt_util import get_answer, get_answer_free, stt, stt_free, tts, tts_free
# python telegram bot
from telegram.ext import (Application, CommandHandler, MessageHandler,
                          filters, CallbackQueryHandler)
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from io import BytesIO
from config_set import config

""" 
На выбор: OpenAI и
GPT4Free https://github.com/xtekky/gpt4free

Пользователь сразу не спрашивая может ввести вопрос
либо текстом либо голосом. Потом появляются две кнопки
для выбора 'GPT 3.5 ответит текстовым и аудио сообщением.
или 'GPT 4.0 только текстовым, но более подробно.'
Т.к. в ответе GPT4 может быть доп. информация (линки и т.д.)
которую нецелесообразно озвучивать.

В файле voice_gpt_util.py, кроме функций чатов GPT, 
по два варианта озвучки из текста и перевода аудио в текст.
"""


TOKEN = config.bot_token.get_secret_value()
allowed_ids = config.allowed_ids
text_choose ='Выберете модель ChatGPT. ' \
             'GPT 3.5 ответит текстовым и аудио сообщением. ' \
             'GPT 4.0 только текстовым, но более подробно.'


def filter_users(update, allowed_ids=allowed_ids):
    return update.message.from_user.id in allowed_ids


def model_keyboard():
    keyboard = [[InlineKeyboardButton("GPT 3.5", callback_data="GPT35"),
                 InlineKeyboardButton("GPT 4.0", callback_data="GPT4")]]
    return InlineKeyboardMarkup(keyboard)


async def start(update, context):
    if filter_users(update):
        await update.message.reply_text('Напишите вопрос или отправьте голосовое сообщение chatGPT')


async def ask_text(update, context):
    if filter_users(update):
        context.bot_data['question'] = update.message.text
        await update.message.reply_text(text_choose, reply_markup=model_keyboard())


async def ask_voice(update, context):
    if filter_users(update):
        msg = await update.message.reply_text('Обрабатывается Аудио сообщение...')
        file = await update.message.voice.get_file()  # аудио файл от пользователя
        byte_voice = await file.download_as_bytearray()
        context.bot_data['question'] = stt_free(BytesIO(byte_voice)) # free version
        # context.bot_data['question'] = stt(BytesIO(byte_voice))    # google-cloud-speech
        await msg.delete()
        await update.message.reply_text(text_choose, reply_markup=model_keyboard())


async def gpt(update, context):
    question = context.bot_data.get('question')
    print(question)
    query = update.callback_query
    await query.edit_message_text('Формируется ответ chatGPT...')
    text_answer = await get_answer_free(question, model=query.data) # GPT35 or GPT4
    # text_answer = await get_answer(question)  # chatGPT official OpenAI
    await query.edit_message_text(text_answer)
    if query.data == 'GPT35': # аудио ответ
        audio = tts_free(text_answer) # free version
        # audio = tts(text_answer)    # google-cloud-texttospeech
        await context.bot.send_audio(chat_id=query.message.chat_id, audio=audio)


def add_handlers(bot):
    bot.add_handler(CommandHandler("start", start, block=False))
    bot.add_handler(MessageHandler(filters.TEXT, ask_text, block=False))
    bot.add_handler(MessageHandler(filters.VOICE, ask_voice, block=False))
    bot.add_handler(CallbackQueryHandler(gpt, block=False))


def main():
    bot = Application.builder().token(TOKEN).build()
    print('Бот запущен...')
    add_handlers(bot)
    bot.run_polling()


if __name__ == "__main__":
    main()