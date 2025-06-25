from keyboards.inline import choose_education_status_info, choose_visitor
from aiogram.dispatcher import FSMContext
from file_service import get_file_path, create_report_file
from datetime import datetime, time
from collections import Counter
from aiogram import types
from loader import dp
import os
from utils.db_api.core import DatabaseService1, User
db = DatabaseService1()

@dp.message_handler(commands=["hisobot"])
async def hisobot(message: types.Message, state: FSMContext):
    now = datetime.now()
    info = await db.get(User, filters={'talim_turi': 'Kunduzgi'})
    # print(info)
    faculty_count = Counter([user.faculty for user in info if user.faculty])
    await create_report_file(faculty_count)
    print(faculty_count.get("Yurisprudensiya"), type(faculty_count))
    # Natijani shakllantirish
    report = "📊 *Fakultetlar bo‘yicha ro‘yxatdan o‘tganlar soni:*\n\n"
    for faculty, count in faculty_count.items():
        report += f"• {faculty} — {count} ta\n"
    print(report, type(report))

    await message.answer(report, parse_mode="Markdown")
    if now.time() >= time(17, 0):

        await message.answer("Yakunlash vaqti!")
        return
