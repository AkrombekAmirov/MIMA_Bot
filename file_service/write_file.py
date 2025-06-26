from file_service.test_file.test_file_path import get_test_file_path, join_test_file
from utils.db_api.core import DatabaseService1, Question
from file_service.file_path import get_file_path
from file_service.hisobot import get_report_file_path
from LoggingService import LoggerService
from openpyxl import load_workbook
from docx2pdf import convert
from datetime import datetime
from os import remove
from os.path import exists
import subprocess
from os.path import dirname

db = DatabaseService1(logger=LoggerService())
YO_NALISHLAR_QATORLARI = {
    "Inson resurslarini boshqarish": 4,
    "Hayot faoliyati xavfsizligi": 5,
    "Yurisprudensiya": 6,
    "Ijtimoiy ish": 7,
    "Menejment": 8,
    "Mehnat muhofazasi va texnika xavfsizligi": 9,
    "Psixologiya": 10,
    "Bugalteriya hisobi": 11,
    "Metrologiya va standartlashtirish": 12,
    "Iqtisodiyot": 13
}


async def create_report_file(jami_data: dict, kunlik_data: dict):
    # try:

    path = await get_file_path("report.xlsx")
    workbook = load_workbook(path)
    sheet = workbook.active
    total_daily = 0
    total_all = 0

    for yo_nalish, row in YO_NALISHLAR_QATORLARI.items():
        # Jami hujjat topshirganlar → F ustun
        jami_val = jami_data.get(yo_nalish, 0)
        sheet[f"E{row}"] = jami_val
        total_all += jami_val

        # Kunlik topshirganlar → E ustun
        kunlik_val = kunlik_data.get(yo_nalish, 0)
        sheet[f"D{row}"] = kunlik_val
        total_daily += kunlik_val
    now = datetime.now()
    formatted_time = now.strftime("%d-%m-%Y")
    sheet["F2"] = f"{formatted_time} holati bo'yicha"
    new_file_name = f"{formatted_time}_hisobot.xlsx"
    new_file_path = await get_report_file_path(new_file_name)

    # 5. Saqlaymiz
    workbook.save(new_file_path)
    workbook.close()
    # await convert_pdf(source_path=new_file_name, target_path=f'{formatted_time}_hisobot')
    return True



async def convert_pdf(source_path, target_path):
    source_path1 = await get_report_file_path(source_path)
    target_dir = dirname(source_path1)

    try:
        subprocess.run([
            'libreoffice', '--headless', '--convert-to', 'pdf', source_path1, '--outdir', target_dir
        ], check=True)

        print("✅ PDF muvaffaqiyatli yaratildi.")
    except subprocess.CalledProcessError as e:
        print(f"❌ LibreOffice orqali PDFga o‘tkazishda xatolik: {e}")


async def write_qabul(row: list):
    try:
        print(row)
        path = await get_file_path("qabul.xlsx")
        print(path)
        workbook = load_workbook(path)
        sheet = workbook.active
        sheet.append(row)  # to'g'ridan-to'g'ri ro'yxat yoziladi
        workbook.save(path)
        return True
    except Exception as e:
        print(f"❌ Excel yozishda xatolik: {e}")
        return False


async def read_file(file_path: str, subject_id: int) -> bool:
    """
    Excel fayldagi savollarni o'qiydi va bazaga qo'shadi.
    - file_path: yuklangan fayl nomi (path olish uchun get_test_file_path ishlatiladi)
    - subject_id: savollar tegishli bo'lgan fan ID
    Qaytaradi True agar yangi savollar qo'shilgan bo'lsa, False aks holda.
    """
    try:
        # 1) Faylni yuklab olish va Workbook ochish
        full_path = await get_test_file_path(name=file_path)
        wb = load_workbook(full_path)
        sheet = wb.active

        # 2) 2-qatordan boshlab barcha satrlarni olish
        rows = list(sheet.iter_rows(min_row=1, values_only=True))
        if not rows:
            print("Faylda savollar topilmadi.")
            return False

        # 3) Birinchi ma'lumot qatori bo'yicha baza tekshiruvi
        first = rows[0]

        if len(first) < 2 or first[1] is None:
            print("Fayl formati noto‘g‘ri yoki birinchi savol yo‘q.")
            return False
        first_text = str(first[1]).strip()
        print(first_text)
        exists = await db.get(Question, filters={"subject_id": subject_id, "text": first_text})
        if exists:
            print("Ma'lumotlar bazasida allaqachon bu savol mavjud:", first_text)
            return False

        # 4) Har bir satr bo‘yicha yangi Question yaratish
        added = 0
        for row in rows:
            # row: tuple (A2, B2, C2, D2, E2, F2, …)
            if not row or len(row) < 1:
                # kam ma'lumotli satrlarni o‘tkazib yuboramiz
                continue
            print(row[0], row[1], row[2], row[3], row[4])

            text = str(row[0] or "").strip()
            opt1 = str(row[1] or "").strip()
            opt2 = str(row[2] or "").strip()
            opt3 = str(row[3] or "").strip()
            opt4 = str(row[4] or "").strip()
            # Misolda to‘g‘ri javob 3-ustunda ekan: row[2]
            correct = opt1

            if not text:
                continue

            await db.add(Question(
                subject_id=subject_id,
                text=text,
                option1=opt1,
                option2=opt2,
                option3=opt3,
                option4=opt4,
                correct_answer=correct
            ))
            added += 1

        print(f"{added} ta savol bazaga qo‘shildi.")
        return added > 0

    except Exception as e:
        print("read_file xatosi:", e)
        return False


async def check_passport_exists(passport_seria: str) -> bool:
    try:
        path = await get_file_path("student_db.xlsx")
        workbook = load_workbook(path)
        sheet = workbook.active

        for row in sheet.iter_rows(min_row=2, values_only=True):  # boshqatorni o'tkazib yuboramiz
            if row[2] == passport_seria:
                return True

        return False

    except Exception as e:
        print(f"❌ Excel yozishda xatolik: {e}")
        return False
