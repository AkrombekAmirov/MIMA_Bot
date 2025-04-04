from aiogram.dispatcher.filters.builtin import CommandStart
from keyboards.inline import choose_visitor, keyboard, choose_admin_1
from utils.db_api.core import DatabaseService
from data.config import engine, ADMIN_M1
from aiogram.types import Message
from loader import dp

db = DatabaseService(engine=engine)


@dp.message_handler(CommandStart())
async def bot_start(message: Message):
    if str(message.from_user.id) == str(ADMIN_M1):
        await message.answer("Xizmat turini tanlang", reply_markup=choose_admin_1)
    elif db.get_user_exists(str(message.from_user.id)):
        await message.answer("Xizmat turini tanlang", reply_markup=choose_visitor)
    elif not db.get_user_exists(str(message.from_user.id)):
        await message.answer("Telegram botiga xush kelibsiz.\nTelegram kontaktangizni yuboring.", reply_markup=keyboard)
