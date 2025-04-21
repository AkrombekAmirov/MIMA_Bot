from openpyxl import load_workbook
from file_service.file_path import get_file_path


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
