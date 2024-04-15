import asyncio
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram import Bot, Dispatcher
from aiogram_dialog import setup_dialogs
from config import settings
from dbase.database import create_db
from keyboards import menu_button
from handlers import first_handlers, dialog


async def start():
    bot = Bot(token=settings.BOT_TOKEN.get_secret_value(),
              default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_routers(
        menu_button.router,
        dialog.main_dialog,
        first_handlers.router,
    )
    setup_dialogs(dp)
    await bot.delete_webhook(drop_pending_updates=True)
    try:
        print('Bot is running...')
        await dp.start_polling(bot)
    finally:
        print('Bot has closed...')
        await bot.session.close()


if __name__  == '__main__':
    asyncio.run(create_db())
    asyncio.run(start())
