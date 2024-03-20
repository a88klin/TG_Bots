from aiogram import Router, F, types
from utils.my_libs import coins_price
from config_set import config

allowed_ids = config.allowed_ids


async def get_ticker_price(message: types.Message):
    await message.answer(coins_price())

async def get_ticker_price2(callback: types.CallbackQuery):
    await callback.message.answer(coins_price())


router = Router()

def register_ticker_price(router):
    router.message.register(get_ticker_price, F.from_user.id.in_(allowed_ids),
                                              F.text.lower()=='coin',
                                              F.text.regexp('(?i)coin'))
    router.callback_query.register(get_ticker_price2, F.from_user.id.in_(allowed_ids),
                                                      F.data=='coin')
