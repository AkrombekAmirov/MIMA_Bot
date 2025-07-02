from file_service import get_report_file_path, create_report_file
from utils.db_api.core import DatabaseService1, User
from aiogram.dispatcher import FSMContext
from datetime import datetime, time
from collections import Counter
from aiogram import types
from loader import dp, bot
import os, asyncio, logging


db = DatabaseService1()


@dp.message_handler(commands=["hisobot"])
async def hisobot_handler(message: types.Message, state: FSMContext):
    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    formatted_time = now.strftime("%d-%m-%Y")

    # 1. Ma'lumotlarni olish (jami va bugungi)
    all_users = await db.get(User, filters={'talim_turi': 'Kunduzgi'})
    daily_users = await db.get(User, filters={'talim_turi': 'Kunduzgi', 'created_date': today_str})
    exam_users = await db.get(User, filters={"talim_turi": "Kunduzgi", "status": True})

    # 2. Fakultet bo‘yicha statistikalar
    total_faculty = Counter(user.faculty for user in all_users if user.faculty)
    daily_faculty = Counter(user.faculty for user in daily_users if user.faculty)
    exam_faculty_counter = Counter(user.faculty for user in exam_users if user.faculty)

    # 3. Excel hisobotini yaratish
    await create_report_file(jami_data=total_faculty, kunlik_data=daily_faculty, exam_data=exam_faculty_counter)

    # 4. Hisobot xabari (jami)
    total_text = "📊 *Fakultetlar bo‘yicha jami ro‘yxatdan o‘tganlar:*\n\n"
    total_count = 0
    for faculty, count in total_faculty.items():
        total_text += f"• {faculty} — {count} ta\n"
        total_count += count
    total_text += f"\n🔢 *Umumiy soni:* {total_count} ta"

    # 5. Hisobot xabari (kunlik)
    daily_text = f"📆 *{formatted_time} kuni ro‘yxatdan o‘tganlar:*\n\n"
    if daily_faculty:
        for faculty, count in daily_faculty.items():
            daily_text += f"• {faculty} — {count} ta\n"
    else:
        daily_text += "Bugun hujjat topshirganlar yo‘q."

    exam_info = f"📆 *{formatted_time} kuni imtihon topshirganlar:*\n\n"
    if exam_faculty_counter:
        for faculty, count in exam_faculty_counter.items():
            exam_info += f"• {faculty} — {count} ta\n"
    else:
        exam_info += "Bugun hujjat topshirganlar yo‘q."

    # 6. Javoblarni yuborish
    await message.answer(total_text, parse_mode="Markdown")
    await message.answer(daily_text, parse_mode="Markdown")
    await message.answer(exam_info, parse_mode="Markdown")

    # 7. Excel faylni yuborish (soat 17:00 dan keyin)
    report_file_name = f"{formatted_time}_hisobot.xlsx"
    report_file_path = await get_report_file_path(report_file_name)

    if report_file_path and os.path.exists(report_file_path):
        await message.answer_document(
            document=types.InputFile(report_file_path),
            caption=f"📎 {formatted_time} kuni uchun hisobot fayli"
        )
        await message.answer("Buyruqni yuboring! /hisobot")
    else:
        await message.answer("⚠️ Excel hisobot fayli topilmadi.")

DEFAULT_BROADCAST_TEXT = (
    "Assalomu alaykum hurmatli abituriyent!\n\n"
    "Mehnat va ijtimoiy munosabatlar akademiyasini tanlaganingiz uchun rahmat!\n\n"
    "📢 Mehnat va ijtimoiy munosabatlar akademiyasida 2025–2026-o‘quv yiliga kirish test imtihonlari "
    "2025-yil 2-iyul sanasidan boshlanishini rasman e’lon qilamiz!\n\n"
    "🕘 Imtihonlar har kuni dushanbadan jumagacha, soat 09:00 dan 16:00 gacha "
    "Akademiya o‘quv binosida bo‘lib o‘tadi."
)

# ✅ Asinxron mass-messaging funksiyasi
async def send_message_to_users(users: list[User], text: str):
    success = 0
    failed = 0

    async def send_one(user: User):
        nonlocal success, failed
        try:
            await bot.send_message(chat_id=int(user.telegram_id), text=text)
            success += 1
        except Exception as e:
            logging.warning(f"⚠️ {user.telegram_id} raqamiga yuborishda xatolik: {e}")
            failed += 1

    # Parallel yuborish
    await asyncio.gather(*(send_one(user) for user in users))
    return success, failed

# ✅ Admin tomonidan yuboriladigan buyruq
@dp.message_handler(commands=["sendmessage"])
async def send_message_handler(message: types.Message, state: FSMContext):
    # 1. Foydalanuvchilarni olish
    users = await db.get(User)

    # 2. Jarayonni boshlanishi haqida adminni xabardor qilish
    await message.answer(f"📨 {len(users)} ta abituriyentga xabar yuborilmoqda...")

    # 3. Xabar yuborish
    success, failed = await send_message_to_users(users, DEFAULT_BROADCAST_TEXT)

    # 4. Natijani chiqarish
    await message.answer(
        f"✅ Yuborish yakunlandi!\n"
        f"🟢 Muvaffaqiyatli: {success}\n"
        f"🔴 Xatolik: {failed}"
    )
