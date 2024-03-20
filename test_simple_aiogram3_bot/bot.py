import asyncio
from aiogram import Bot, Dispatcher
from config_set import config

from handlers import other
from handlers.other import register_other
from handlers import ticker_price
from handlers.ticker_price import register_ticker_price
from handlers import moon
from handlers.moon import register_moon
from handlers import weather
from handlers.weather import register_city_weather


def include_all_router(dp):
    dp.include_router(other.router)
    dp.include_router(ticker_price.router)
    dp.include_router(moon.router)
    dp.include_router(weather.router)

def register_all_handlers():
    register_other(other.router)
    register_ticker_price(ticker_price.router)
    register_moon(moon.router)
    register_city_weather(weather.router)

# ***********************************************************
async def main():
    bot = Bot(token=config.bot_token.get_secret_value())
    dp = Dispatcher()

    include_all_router(dp)
    register_all_handlers()

    print('Bot is running...')
    await bot.delete_webhook(drop_pending_updates=True)
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())