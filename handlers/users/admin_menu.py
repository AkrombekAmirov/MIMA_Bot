from keyboards.inline.keyboards_inline import choose_admin_1, response_admin, subject_
from utils.db_api.core import DatabaseService1, User, Subject, Faculty, FacultyBlock
from file_service import join_test_file, read_file
from aiogram.dispatcher import FSMContext
from LoggingService import LoggerService
from aiogram import types
from loader import dp

db = DatabaseService1(logger=LoggerService())


@dp.callback_query_handler(text='test_enter_admin')
async def answer(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("Fan nomini tanlang!", reply_markup=subject_)


@dp.callback_query_handler(
    lambda call: call.data in ['info_law_1', 'info_law_2', 'info_law_3', 'info_law_4', 'info_law_5', 'info_law_6',
                               'info_law_7', 'info_law_8', 'info_law_9', 'info_law_10'])
async def subject(call: types.CallbackQuery, state: FSMContext):
    await state.update_data({"faculty_": call.data})
    await call.message.answer("Tast tayyorlangan fileni yuboring!\nEslatma file nomiga etibor bering!")


@dp.message_handler(content_types=types.ContentTypes.DOCUMENT, state="*")
async def handle_file(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await dp.bot.download_file(
        (await dp.bot.get_file(message.document.file_id)).file_path,
        await join_test_file(file_name=message.document.file_name)
    )
    await message.answer("Fayl saqlandi!")
    if not await read_file(file_path=message.document.file_name, subject_id=int(data.get('faculty_')[-1])):
        await message.answer("Testlar bazasiga qo'shildi", reply_markup=choose_admin_1)
        await state.reset_state(with_data=False)

# @dp.callback_query_handler(lambda call: call.data in ['delete_no_admin'])
# async def answer(call: types.CallbackQuery, state: FSMContext):
#     await call.message.delete()
#     await call.message.answer(
#         "Foydalanuvchini o'chirish uchun pasport seria va raqamini kiriting!\nNamuna: AA1234567")
#
#
# @dp.message_handler(types.Message)
# async def adminic(message: types.Message, state: FSMContext):
#     await state.update_data({"passport": message.text})
#     if not db.get():
#         await message.answer("Bunday foydalanuvchi topilmadi!", reply_markup=choose_admin_1)
#     elif db.get_user_by_passport(message.text):
#         user = db.get_user_by_passport(message.text)
#         print(user.name, user.faculty, user.contract_number)
#         await message.answer(f"F.I.Sh:{user.name}\n"
#                              f"Yonalish: {user.faculty}\n"
#                              f"Contract number: {user.contract_number}\n"
#                              f"Raqam: {user.telegram_number}\n"
#                              f"Passport: {user.passport}\nRostan o'chirasizmi?", reply_markup=response_admin)
#
#
# @dp.callback_query_handler(lambda call: call.data in ["yes_admin", "no_admin"])
# async def adminic(call: types.CallbackQuery, state: FSMContext):
#     if call.data == "yes_admin":
#         data = await state.get_data()
#         db.delete_user(data.get("passport"))
#         await call.message.answer("Foydalanuvchi o'chirildi!", reply_markup=choose_admin_1)
#     elif call.data == "no_admin":
#         await call.message.answer("Foydalanuvchi o'chirilmadi!", reply_markup=choose_admin_1)
#     await state.reset_state(with_data=True)
