import asyncio
from aiogram import Bot, Dispatcher
from settings import settings
from keyboards import menu_button
from handlers import handlers


BOT_TOKEN = settings.bot_token.get_secret_value()

async  def start():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.include_routers(
        menu_button.router,
        handlers.router,
    )

    await bot.delete_webhook(drop_pending_updates=True)
    try:
        print('Bot is running...')
        await dp.start_polling(bot)
    finally:
        print('Bot has closed...')
        await bot.session.close()


if __name__  == '__main__':
    asyncio.run(start())
