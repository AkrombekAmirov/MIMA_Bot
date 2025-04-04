from keyboards.inline.keyboards_inline import choose_admin_1, response_admin
from utils.db_api.core import DatabaseService
from aiogram.dispatcher import FSMContext
from data.config import engine, ADMINS
from loader import dp, bot
from aiogram import types
import logging

logging.basicConfig(filename='bot.log', filemode='w', level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

db = DatabaseService(engine=engine)


@dp.callback_query_handler(lambda call: call.data in ['delete_no_admin'])
async def answer(call: types.CallbackQuery, state: FSMContext):
        await call.message.delete()
        await call.message.answer(
            "Foydalanuvchini o'chirish uchun pasport seria va raqamini kiriting!\nNamuna: AA1234567")

@dp.message_handler(types.Message)
async def adminic(message: types.Message, state: FSMContext):
    await state.update_data({"passport": message.text})
    if not db.get_user_by_passport(message.text):
        await message.answer("Bunday foydalanuvchi topilmadi!", reply_markup=choose_admin_1)
    elif db.get_user_by_passport(message.text):
        user = db.get_user_by_passport(message.text)
        print(user.name, user.faculty, user.contract_number)
        await message.answer(f"F.I.Sh:{user.name}\n"
                             f"Yonalish: {user.faculty}\n"
                             f"Contract number: {user.contract_number}\n"
                             f"Raqam: {user.telegram_number}\n"
                             f"Passport: {user.passport}\nRostan o'chirasizmi?", reply_markup=response_admin)

@dp.callback_query_handler(lambda call: call.data in ["yes_admin", "no_admin"])
async def adminic(call: types.CallbackQuery, state: FSMContext):
    if call.data == "yes_admin":
        data = await state.get_data()
        db.delete_user(data.get("passport"))
        await call.message.answer("Foydalanuvchi o'chirildi!", reply_markup=choose_admin_1)
    elif call.data == "no_admin":
        await call.message.answer("Foydalanuvchi o'chirilmadi!", reply_markup=choose_admin_1)
    await state.reset_state(with_data=True)
