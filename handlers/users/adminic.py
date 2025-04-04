import logging
import asyncio
from uuid import uuid4
from datetime import datetime
from aiogram import types
from aiogram.dispatcher import FSMContext
from loader import dp, bot
from data.config import engine, ADMIN_M1, ADMINS
from utils.db_api.core import DatabaseService
from keyboards.inline.keyboards_inline import choose_visitor
from keyboards.inline.Dictionary import faculty_file_map1
from states.button import Form
import aiofiles

# Loggingni sozlash
logging.basicConfig(filename='bot.log', filemode='w', level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

db = DatabaseService(engine=engine)


async def send_error_message(admin_ids, message):
    """Administratorlarga xatolik haqida xabar yuborish"""
    try:
        await bot.send_message(ADMIN_M1, message)
    except Exception as e:
        logging.error("Adminlarga xatolik haqida xabar yuborishda xato: %s", e)


@dp.callback_query_handler(lambda c: c.data.startswith("approve_") or c.data.startswith("reject_"))
async def process_application_response(call: types.CallbackQuery, state: FSMContext):
    try:
        data = call.data.split("_")
        if len(data) != 4:
            raise ValueError("Kutilmagan ma'lumot formati")

        action, user_id, message_id, faculty = data

        if action == "approve":
            await bot.send_message(
                user_id,
                "Sizning arizangiz tasdiqlandi! ✅\nSizning arizangizga binoan tuzilgan quyidagi shartnoma orqali to'lovni amalga oshirishingiz mumkin."
            )
            await func_qrcode(url=message_id, name=user_id, status=True)
            await create_file(telegram_id=user_id, faculty=faculty)
            await call.message.edit_text("Ariza tasdiqlandi. ✅")

        elif action == "reject":
            await call.message.delete()
            await call.message.answer("Iltimos, rad etish sababini yozing:")
            await state.update_data(user_id=user_id)
            await Form.reason.set()

    except Exception as e:
        logging.error("process_application_response funksiyasida xato: %s", e)
        await call.answer("Xatolik yuz berdi. Qaytadan urinib ko‘ring.")


@dp.message_handler(state=Form.reason)
async def get_rejection_reason(message: types.Message, state: FSMContext):
    rejection_reason = message.text
    data = await state.get_data()
    user_id = data.get("user_id")

    await bot.send_message(
        user_id,
        f"Sizning arizangiz rad etildi. ❌\nSabab: {rejection_reason}",
        reply_markup=choose_visitor
    )
    await message.answer(f"Rad etish sababi foydalanuvchiga yuborildi: {rejection_reason}")
    await state.finish()


async def create_file(telegram_id, faculty):
    try:
        # Foydalanuvchini tekshirish
        user_ = db.get_user_by_telegram_id(telegram_id=telegram_id)
        if not user_:
            logging.warning("Foydalanuvchi topilmadi: %s", telegram_id)
            await send_error_message(ADMINS, f"Foydalanuvchi topilmadi: {telegram_id}")
            return

        contract_number = str(db.get_max_contract_number())

        _uuid = str(uuid4())
        _ariza_uuid = str(uuid4())

        # Qabul yozuvini yaratish
        await write_qabul([
            [user_.name, user_.faculty, user_.passport, contract_number,
             user_.viloyat, user_.tuman, user_.telegram_number,
             datetime.now().strftime("%d-%m-%Y")]
        ])

        await func_qrcode(url=_uuid, name=user_.name, status=True)

        # Shartnoma faylini yaratish
        contract_path = await get_file_path(name=f"file_shartnoma/{user_.name}.pdf")
        await process_contract(
            name=user_.name,
            faculty=user_.faculty,
            passport=user_.passport,
            number=user_.telegram_number,
            address=f"{user_.viloyat}, {user_.tuman}",
            contract_number=contract_number,
            file_name=await get_file_database_path(name=faculty_file_map1.get(faculty))
        )

        # Shartnomani foydalanuvchiga jo'natish
        response = await dp.bot.send_document(telegram_id, types.InputFile(contract_path))

        # Ma'lumotlarni yangilash
        db.update_(
            telegram_id=telegram_id,
            updated_fields={
                "contract_number": contract_number,
                "telegram_file_id": response.document.file_id,
                "file_id": _uuid,
                "ariza_id": _ariza_uuid,
                "status": "True"
            }
        )

        # Fayllarni saqlash uchun yordamchi funksiya
        await save_user_files(user_, _uuid, _ariza_uuid, contract_number)

        # Administratorlarga hujjatlarni jo'natish
        await send_admin_documents(user_, response, contract_number)

    except Exception as e:
        logging.error("create_file funksiyasida xato: %s", e)
        await send_error_message(ADMINS, "Shartnoma faylini yaratishda xatolik yuz berdi.")


async def save_user_files(user_, uuid, ariza_uuid, contract_number):
    """Foydalanuvchi uchun fayllarni yaratish va saqlash"""
    for file_name, file_uuid in [("file_shartnoma", uuid), ("file_ariza", ariza_uuid)]:
        file_path = await get_file_path(name=f"{file_name}/{user_.name}.pdf")
        with open(file_path, "rb") as file:
            await file_create_(
                user_id=[f"{user_.passport}", file_uuid, contract_number],
                images=[(file, "application/pdf")]
            )



async def send_admin_documents(user_, response, contract_number):
    """Administratorlarga hujjatlarni jo'natish"""
    qabul_path = await get_file_database_path(name='qabul.xlsx')
    await asyncio.gather(
        dp.bot.send_document(ADMIN_M1, types.InputFile(qabul_path)),
        dp.bot.send_document(ADMIN_M1, response.document.file_id),
        dp.bot.send_document(ADMIN_M1, user_.telegram_ariza_id),
        dp.bot.send_message(
            ADMIN_M1,
            f"F.I.Sh:<b>{user_.name}</b>\nPassport:<b>{user_.passport}</b>\n"
            f"Shartnoma raqami:<b>{contract_number}</b>\n"
            f"Fakultet:<b>{user_.faculty}</b>\nTelegram raqami:{user_.telegram_number}\n"
            f"Viloyat:{user_.viloyat}\nTuman:{user_.tuman}"
        )
    )
