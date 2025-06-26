from file_service import get_report_file_path, create_report_file
from utils.db_api.core import DatabaseService1, User
from aiogram.dispatcher import FSMContext
from datetime import datetime, time
from collections import Counter
from aiogram import types
from loader import dp
import os


db = DatabaseService1()


@dp.message_handler(commands=["hisobot"])
async def hisobot_handler(message: types.Message, state: FSMContext):
    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    formatted_time = now.strftime("%d-%m-%Y")

    # 1. Ma'lumotlarni olish (jami va bugungi)
    all_users = await db.get(User, filters={'talim_turi': 'Kunduzgi'})
    daily_users = await db.get(User, filters={'talim_turi': 'Kunduzgi', 'created_date': today_str})

    # 2. Fakultet bo‘yicha statistikalar
    total_faculty = Counter(user.faculty for user in all_users if user.faculty)
    daily_faculty = Counter(user.faculty for user in daily_users if user.faculty)

    # 3. Excel hisobotini yaratish
    await create_report_file(jami_data=total_faculty, kunlik_data=daily_faculty)

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

    # 6. Javoblarni yuborish
    await message.answer(total_text, parse_mode="Markdown")
    await message.answer(daily_text, parse_mode="Markdown")

    # 7. Excel faylni yuborish (soat 17:00 dan keyin)
    report_file_name = f"{formatted_time}_hisobot.xlsx"
    report_file_path = await get_report_file_path(report_file_name)

    if report_file_path and os.path.exists(report_file_path):
        await message.answer_document(
            document=types.InputFile(report_file_path),
            caption=f"📎 {formatted_time} kuni uchun hisobot fayli"
        )
    else:
        await message.answer("⚠️ Excel hisobot fayli topilmadi.")
