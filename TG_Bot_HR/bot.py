import asyncio
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram import Bot, Dispatcher
from aiogram.fsm.strategy import FSMStrategy
from aiogram.fsm.storage.memory import MemoryStorage
from settings import settings
from keyboards import menu_button
from handlers import handlers, questions_fsm
from update_vacancies import update_vacancies
import os


def create_data_dirs():
    os.makedirs(settings.resumes_json_files, exist_ok=True)
    os.makedirs(settings.pdf_report_files, exist_ok=True)


async  def start():
    bot = Bot(token=settings.bot_token.get_secret_value(),
              default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage(),
                    fsm_strategy=FSMStrategy.USER_IN_CHAT) # по умолчанию

    dp.include_routers(
        menu_button.router,
        handlers.router,
        questions_fsm.router,
    )

    await bot.delete_webhook(drop_pending_updates=True)
    try:
        print('Bot is running...')
        await dp.start_polling(bot)
    finally:
        print('Bot has closed...')
        await bot.session.close()


if __name__  == '__main__':
    update_vacancies()
    create_data_dirs()
    asyncio.run(start())
