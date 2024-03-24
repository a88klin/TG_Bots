from aiogram import Router, Bot
from aiogram.types import BotCommand


router = Router()

@router.startup()
async def set_menu_botton(bot: Bot):
    # Список с командами и их описанием для кнопки menu
    main_menu_commands = [
        BotCommand(command='/start', description='Start')]
    await bot.set_my_commands(main_menu_commands)
