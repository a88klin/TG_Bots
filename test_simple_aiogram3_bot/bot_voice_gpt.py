import asyncio
from aiogram import Bot, Dispatcher, types, F
from config_set import config
from utils.my_libs import stt_free, ask_gpt

bot = Bot(token=config.bot_token.get_secret_value())
dp = Dispatcher()
allowed_ids = config.allowed_ids


@dp.message(F.from_user.id.in_(allowed_ids), F.voice)
async def voice_msg(message: types.Voice):
    msg = await message.answer('Обработка голосового сообщения...')
    file_id = message.voice.file_id
    # await bot.download(message.voice, destination='file.ogg')
    file_info = await bot.get_file(file_id=file_id)
    file = await bot.download_file(file_info.file_path)  # _io.BytesIO object

    ask_text = stt_free(file)
    if ask_text:
        await msg.edit_text(f'Ваш вопрос: {ask_text}')

    msg2 = await message.answer('Формирование ответа ChatGPT...')
    answer_gpt = await ask_gpt(ask_text, model='GPT35')
    if answer_gpt:
        await msg2.edit_text(answer_gpt)


# ***********************************************************
async def main():
    print('Bot is running...')
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
