from openpyxl import load_workbook
from file_service.test_file.test_file_path import get_test_file_path, join_test_file
from file_service.file_path import get_file_path
from utils.db_api.core import DatabaseService1, Question
from LoggingService import LoggerService

db = DatabaseService1(logger=LoggerService())


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

async def read_file(file_path: str, subject_id: int):
    try:
        sheet = load_workbook(await get_test_file_path(name=file_path)).active
        if await db.get(Question, filters={"subject_id": subject_id, "text": next(sheet.iter_rows(values_only=True))[1]}):
            print("Malumot bazasida savol mavjud")
            return None
        else:
            print("Malumot bazasida savol mavjud emas")
            for row in sheet.iter_rows(3, values_only=True):
                await db.add(Question(subject_id=subject_id, text=row[1], option1=str(row[2]), option2=str(row[3]), option3=str(row[4]),
                                      option4=str(row[5]), correct_answer=str(row[2])))
    except Exception as e:
        print(e)
        return None


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
