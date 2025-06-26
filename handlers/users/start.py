from aiogram.dispatcher.filters.builtin import CommandStart
from keyboards.inline import choose_visitor, keyboard, choose_admin_1
from utils.db_api.core import DatabaseService1, User
from data.config import engine, ADMIN_M1, ADMINS
from LoggingService import LoggerService
from aiogram.types import Message
from loader import dp

# logger = LoggerService().get_logger()
db = DatabaseService1(logger=LoggerService())


@dp.message_handler(CommandStart())
async def bot_start(message: Message):
    if str(message.from_user.id) == str('685098494'):
        await message.answer("Buyruqni yuboring! /hisobot")
    elif str(message.from_user.id) == str(ADMIN_M1):
        await message.answer("Xizmat turini tanlang", reply_markup=choose_admin_1)
    elif await db.get(User, filters={'telegram_id': str(message.from_user.id)}):
        await message.answer("Xizmat turini tanlang", reply_markup=choose_visitor)
    elif not await db.get(User, filters={'telegram_id': str(message.from_user.id)}):
        await message.answer("Telegram botiga xush kelibsiz.\nTelegram kontaktangizni yuboring.", reply_markup=keyboard)
