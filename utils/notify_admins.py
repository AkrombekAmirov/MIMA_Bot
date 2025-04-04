import logging

from aiogram import Dispatcher

from data.config import ADMIN_M2


async def on_startup_notify(dp: Dispatcher):
    try:
        await dp.bot.send_message(ADMIN_M2, "Bot ishga tushdi. /start")

    except Exception as err:
        logging.exception(err)
