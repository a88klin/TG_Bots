from aiogram import Router, Bot
from aiogram.types import BotCommand


router = Router()

@router.startup()
async def set_menu_botton(bot: Bot):
    # Для кнопки Menu
    main_menu_commands = [
        BotCommand(command='/start', description='Start'),
        BotCommand(command='/clear', description='Clear context memory')
    ]
    await bot.set_my_commands(main_menu_commands)
