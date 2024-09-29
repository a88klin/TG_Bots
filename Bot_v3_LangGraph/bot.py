import asyncio
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram import Bot, Dispatcher
import handlers
from set.config import config


bot = Bot(token=config.BOT_TOKEN.get_secret_value(),
          default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
dp = Dispatcher()
dp.include_routers(handlers.router,)


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    try:
        print('Bot is running...')
        await dp.start_polling(bot)
    finally:
        print('Bot has closed...')
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
