from aiogram import Router, F, types
from utils.my_libs import moon_and_nday
from config_set import config

allowed_ids = config.allowed_ids


async def moon_phase(message: types.Message):
    await message.answer(moon_and_nday())

async def moon_phase2(callback: types.CallbackQuery):
    await callback.message.answer(moon_and_nday())


router = Router()

def register_moon(router):
    router.message.register(moon_phase, F.from_user.id.in_(allowed_ids),
                                        F.text.lower()=='moon')
    router.callback_query.register(moon_phase2, F.from_user.id.in_(allowed_ids),
                                                F.data=='moon')
