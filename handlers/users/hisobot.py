from file_service import get_report_file_path, create_report_file, create_report_all_file, create_report_by_faculty_files
from utils.db_api.core import DatabaseService1, User, Result, Subject
from aiogram.dispatcher import FSMContext
from collections import Counter
from datetime import datetime
import os, asyncio, logging
from loader import dp, bot
from aiogram import types
from json import loads

db = DatabaseService1()
now = datetime.now()
today_str = now.strftime("%Y-%m-%d")
formatted_time = now.strftime("%d-%m-%Y")


@dp.message_handler(commands=["hisobot"])
async def hisobot_handler(message: types.Message, state: FSMContext):
    # 1. Ma'lumotlarni olish (jami va bugungi)
    all_users = await db.get(User, filters={'talim_turi': 'Kunduzgi'})
    daily_users = await db.get(User, filters={'talim_turi': 'Kunduzgi', 'created_date': today_str})
    exam_users = await db.get(User, filters={"talim_turi": "Kunduzgi", "status": True, 'exam_day': today_str})
    exam_all = await db.get(User, filters={"talim_turi": "Kunduzgi", "status": True})

    # 2. Fakultet bo‘yicha statistikalar
    total_faculty = Counter(user.faculty for user in all_users if user.faculty)
    daily_faculty = Counter(user.faculty for user in daily_users if user.faculty)
    exam_faculty_counter = Counter(user.faculty for user in exam_users if user.faculty)
    exam_faculty_all_counter = Counter(user.faculty for user in exam_all if user.faculty)

    # 3. Excel hisobotini yaratish
    await create_report_file(jami_data=total_faculty, kunlik_data=daily_faculty, exam_data=exam_faculty_counter, exam_all_data=exam_faculty_all_counter)

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


BLOCK_WEIGHTS = {1: 3, 2: 2, 3: 1}
BLOCK_TOTAL = {1: 60, 2: 30, 3: 10}
BLOCK_QUESTION_COUNTS = {1: 20, 2: 15, 3: 10}  # doimiy savollar soni


@dp.message_handler(commands=["getreport"])
async def get_report_handler(message: types.Message, state: FSMContext):
    try:
        users = await db.get(User, filters={"status": True})
        results = await db.get(Result)
        subjects = await db.get(Subject)
        subject_map = {str(s.subject_val): s.name for s in subjects}
        result_map = {(str(r.user_id), r.block_number): r for r in results}

        rows = []

        for user in sorted(users, key=lambda x: x.exam_day or x.created_date):
            user_id = str(user.id)

            row = {
                "name": user.name,
                "faculty": user.faculty,
                "exam_day": user.exam_day or user.created_date,
                "total_ball": 0
            }

            has_result = False  # userda hech bo‘lmasa 1ta blok natija bo‘lishi kerak

            for block in [1, 2, 3]:
                res = result_map.get((user_id, block))
                correct = wrong = 0
                subject_name = ""

                if res:
                    has_result = True
                    correct = res.correct_answers
                    wrong = res.wrong_answers
                    subject_name = subject_map.get(str(res.subject_id), "Noma'lum fan")

                block_weight = BLOCK_WEIGHTS.get(block, 1)
                total_questions = BLOCK_QUESTION_COUNTS.get(block, 0)
                block_total_ball = BLOCK_TOTAL.get(block, 0)

                ball = correct * block_weight
                accuracy = round((correct / total_questions * 100), 1) if total_questions > 0 else 0

                row[f"block_{block}_jami_ball"] = block_total_ball
                row[f"block_{block}_ball"] = ball
                row[f"block_{block}_total_questions"] = total_questions
                row[f"block_{block}_correct"] = correct
                row[f"block_{block}_wrong"] = wrong
                row[f"block_{block}_accuracy"] = f"{accuracy}%"
                row[f"block_{block}_subject"] = subject_name

                row["total_ball"] += ball

            if has_result:
                rows.append(row)
            else:
                print(f"⚠️ Foydalanuvchida natijalar yo'q: {user.name} (ID: {user_id})")

        if rows:
            file_path = await create_report_all_file(rows, 'all')
            # report_files = await create_report_by_faculty_files(rows)
            # for file in report_files:
            #     await message.answer_document(open(file, "rb"), caption="📘 Fakultet bo‘yicha hisobot")
            await message.answer_document(open(file_path, "rb"), caption="📊 Hisobot fayli tayyor.")
        else:
            await message.answer("⚠️ Hech qanday natija topilmadi.")
    except Exception as e:
        print(f"❌ get_report_handler xatolik: {e}")
        await message.answer("Hisobotni yaratishda xatolik yuz berdi.")


@dp.message_handler(commands=["getreport_today"])
async def get_report_today_handler(message: types.Message, state: FSMContext):
    try:
        users = await db.get(User, filters={"status": True})
        results = await db.get(Result)
        subjects = await db.get(Subject)

        subject_map = {str(s.subject_val): s.name for s in subjects}
        result_map = {(str(r.user_id), r.block_number): r for r in results}

        rows = []

        for user in sorted(users, key=lambda x: x.exam_day or x.created_date):
            exam_date = user.exam_day
            if exam_date != today_str:
                continue  # faqat bugungi imtihonlar

            user_id = str(user.id)
            row = {
                "name": user.name,
                "faculty": user.faculty,
                "exam_day": exam_date,
                "total_ball": 0
            }

            has_result = False

            for block in [1, 2, 3]:
                res = result_map.get((user_id, block))
                correct = wrong = 0
                subject_name = ""

                if res:
                    has_result = True
                    correct = res.correct_answers
                    wrong = res.wrong_answers
                    subject_name = subject_map.get(str(res.subject_id), "Noma'lum fan")

                block_weight = BLOCK_WEIGHTS.get(block, 1)
                total_questions = BLOCK_QUESTION_COUNTS.get(block, 0)
                block_total_ball = BLOCK_TOTAL.get(block, 0)

                ball = correct * block_weight
                accuracy = round((correct / total_questions * 100), 1) if total_questions > 0 else 0

                row[f"block_{block}_jami_ball"] = block_total_ball
                row[f"block_{block}_ball"] = ball
                row[f"block_{block}_total_questions"] = total_questions
                row[f"block_{block}_correct"] = correct
                row[f"block_{block}_wrong"] = wrong
                row[f"block_{block}_accuracy"] = f"{accuracy}%"
                row[f"block_{block}_subject"] = subject_name

                row["total_ball"] += ball

            if has_result:
                rows.append(row)

        if rows:
            file_path = await create_report_all_file(rows, 'daily')
            await message.answer_document(open(file_path, "rb"), caption="📊 Bugungi imtihon natijalari tayyor.")
        else:
            await message.answer("📭 Bugungi kunda hech kim imtihon topshirmagan.")

    except Exception as e:
        print(f"❌ get_report_today_handler xatolik: {e}")
        await message.answer("Hisobotni yaratishda xatolik yuz berdi.")


# +998334280898


@dp.message_handler(commands=["getreport"])
async def get_report_handler(message: types.Message, state: FSMContext):
    users = await db.get(User, filters={"status": True})
    results = await db.get(Result)
    subjects = await db.get(Subject)

    subject_map = {s.id: s.name for s in subjects}
    result_map = {(r.user_id, r.block_number): r for r in results}

    rows = []
    for user in sorted(users, key=lambda x: x.exam_day or x.created_date):
        row = {
            "name": user.name,
            "passport": user.passport,
            "telegram_id": user.telegram_id,
            "faculty": user.faculty,
            "exam_day": user.exam_day or user.created_date,
            "total_ball": 0
        }
        for block in [1, 2, 3]:
            res = result_map.get((str(user.id), block))
            total = correct = 0
            subject_name = ""

            if res:
                total = len(loads(res.question_ids)) if res.question_ids else 0
                correct = res.correct_answers
                subject_name = subject_map.get(res.subject_id, "")

            ball = correct * BLOCK_WEIGHTS[block]
            accuracy = round((correct / total * 100), 1) if total > 0 else 0
            row[f"block_{block}_total"] = total
            row[f"block_{block}_correct"] = correct
            row[f"block_{block}_accuracy"] = accuracy
            row[f"block_{block}_subject"] = subject_name
            row["total_ball"] += ball

        rows.append(row)


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
            print(f"⚠️ user_id:{user.telegram_id}, telefon raqami: {user.telegram_number}, F.I.Sh:{user.name} xatolik: {e}\n")

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
