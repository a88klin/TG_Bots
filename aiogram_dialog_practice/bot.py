import asyncio
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram import Bot, Dispatcher
from aiogram_dialog import setup_dialogs
from config import settings

# ПОДКЛЮЧИТЬ ОДИН НУЖНЫЙ ФАЙЛ ДИАЛОГА ИЗ ПАПКИ 'dialogs' и нужные роутеры

# from dialogs.dialog9_transitions import router_handlers, start_dialog
from dialogs.dialog11_widgets_transitions import router_handlers, start_dialog, second_dialog


BOT_TOKEN = settings.BOT_TOKEN.get_secret_value()

async def start():
    bot = Bot(token=BOT_TOKEN,
              default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    dp.include_routers(router_handlers,
                       start_dialog,
                       second_dialog,
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
    asyncio.run(start())