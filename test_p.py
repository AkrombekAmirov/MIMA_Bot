import asyncio
from utils import DatabaseService1
from utils.db_api.models import Question, Subject

# Bu yerga o‘zingiz tuzgan matematika savollari JSON ro‘yxatini joylang

GOSPRAVO = [
    {
        "question": "Что является основным законом Республики Узбекистан?",
        "options": ["Конституция", "Указ", "Постановление", "Закон"],
        "correct_answer": "Конституция"
    },
    {
        "question": "Какой орган осуществляет законодательную власть в Республике Узбекистан?",
        "options": ["Олий Мажлис", "Президент", "Кабинет Министров", "Суд"],
        "correct_answer": "Олий Мажлис"
    },
    {
        "question": "Что означает принцип верховенства закона?",
        "options": ["Все подчиняются закону", "Закон меняется по желанию", "Граждане могут игнорировать закон", "Закон действует выборочно"],
        "correct_answer": "Все подчиняются закону"
    },
    {
        "question": "Какой возраст установлен для участия в выборах?",
        "options": ["18 лет", "16 лет", "21 год", "20 лет"],
        "correct_answer": "18 лет"
    },
    {
        "question": "Кто имеет право издавать указы?",
        "options": ["Президент", "Министр", "Суд", "Парламент"],
        "correct_answer": "Президент"
    },
    {
        "question": "Что регулирует гражданское право?",
        "options": ["Имущественные и личные неимущественные отношения", "Уголовные наказания", "Налогообложение", "Избирательные права"],
        "correct_answer": "Имущественные и личные неимущественные отношения"
    },
    {
        "question": "Как называется право на труд?",
        "options": ["Социальное право", "Экономическое право", "Гражданское право", "Административное право"],
        "correct_answer": "Социальное право"
    },
    {
        "question": "Что такое юридическая ответственность?",
        "options": ["Обязанность нести наказание за правонарушение", "Право на свободу", "Обязанность работать", "Налогообложение"],
        "correct_answer": "Обязанность нести наказание за правонарушение"
    },
    {
        "question": "Что регулирует уголовное право?",
        "options": ["Преступления и наказания", "Семейные споры", "Наследственные дела", "Гражданские дела"],
        "correct_answer": "Преступления и наказания"
    },
    {
        "question": "Как называется документ, удостоверяющий личность гражданина?",
        "options": ["Паспорт", "Свидетельство", "Разрешение", "Приказ"],
        "correct_answer": "Паспорт"
    },
    {
        "question": "Что такое правоспособность?",
        "options": ["Способность иметь права и обязанности", "Способность бегать", "Способность платить налоги", "Способность голосовать"],
        "correct_answer": "Способность иметь права и обязанности"
    },
    {
        "question": "Кто утверждает государственный бюджет?",
        "options": ["Олий Мажлис", "Президент", "Министерство финансов", "Прокуратура"],
        "correct_answer": "Олий Мажлис"
    },
    {
        "question": "Что входит в обязанности суда?",
        "options": ["Разрешать правовые споры", "Издавать законы", "Принимать бюджет", "Создавать партии"],
        "correct_answer": "Разрешать правовые споры"
    },
    {
        "question": "Какой документ определяет структуру власти в государстве?",
        "options": ["Конституция", "Приказ", "Указ", "Постановление"],
        "correct_answer": "Конституция"
    },
    {
        "question": "Что такое административное право?",
        "options": ["Отрасль права, регулирующая деятельность исполнительных органов", "Уголовное право", "Семейное право", "Финансовое право"],
        "correct_answer": "Отрасль права, регулирующая деятельность исполнительных органов"
    },
    {
        "question": "Кто может быть Президентом Республики Узбекистан?",
        "options": ["Гражданин РУз старше 35 лет", "Иностранный гражданин", "Судья", "Любой депутат"],
        "correct_answer": "Гражданин РУз старше 35 лет"
    },
    {
        "question": "Что такое правовая норма?",
        "options": ["Обязательное правило поведения", "Мнение эксперта", "Пожелание депутата", "Моральный принцип"],
        "correct_answer": "Обязательное правило поведения"
    },
    {
        "question": "Какое наказание применяется при совершении преступления?",
        "options": ["Уголовное наказание", "Гражданское взыскание", "Дисциплинарное замечание", "Моральное порицание"],
        "correct_answer": "Уголовное наказание"
    },
    {
        "question": "Как называется способность действовать от своего имени?",
        "options": ["Дееспособность", "Правоспособность", "Право", "Обязанность"],
        "correct_answer": "Дееспособность"
    },
    {
        "question": "Кто может участвовать в выборах?",
        "options": ["Граждане старше 18 лет", "Иностранцы", "Несовершеннолетние", "Только мужчины"],
        "correct_answer": "Граждане старше 18 лет"
    },
    {
        "question": "Какие бывают виды прав?",
        "options": ["Личные, политические, социальные", "Физические, моральные", "Бюджетные, налоговые", "Технические, юридические"],
        "correct_answer": "Личные, политические, социальные"
    },
    {
        "question": "Что делает прокуратура?",
        "options": ["Надзирает за соблюдением закона", "Издаёт законы", "Создаёт партии", "Контролирует бизнес"],
        "correct_answer": "Надзирает за соблюдением закона"
    },
    {
        "question": "Какой орган осуществляет правосудие?",
        "options": ["Суд", "Парламент", "Президент", "Прокуратура"],
        "correct_answer": "Суд"
    },
    {
        "question": "Что регулирует трудовое право?",
        "options": ["Отношения между работником и работодателем", "Бюджетные отношения", "Налоги", "Административные штрафы"],
        "correct_answer": "Отношения между работником и работодателем"
    },
    {
        "question": "Что такое гражданское общество?",
        "options": ["Совокупность свободных организаций и институтов", "Военная структура", "Финансовая система", "Правительство"],
        "correct_answer": "Совокупность свободных организаций и институтов"
    },
    {
        "question": "Какая норма является обязательной к исполнению?",
        "options": ["Юридическая норма", "Мнение юриста", "Рекомендация", "Комментарий"],
        "correct_answer": "Юридическая норма"
    },
    {
        "question": "Кто имеет право на свободу слова?",
        "options": ["Каждый гражданин", "Только журналисты", "Только депутаты", "Только Президент"],
        "correct_answer": "Каждый гражданин"
    }
]





async def seed_math_questions():
    db = DatabaseService1()
    # await db.add(Subject(name="Nemis tili", subject_val='14', language="O'zbek tili"))
    # await db.add(Subject(name="Fransuz tili", subject_val='15', language="Rus tili"))
    inserted = 0
    for item in GOSPRAVO:
        text = item["question"].strip()
        # agar allaqachon bunday savol bo‘lsa o‘tib ketamiz
        # exists = await db.get(Question, filters={"subject_id": subject_id, "text": text})
        # if exists:
        #     continue

        opts = item["options"]
        if len(opts) != 4:
            print(f"Skipping «{text}»: 4 ta option talab qilinadi.")
            continue

        q = Question(
            subject_id=13,
            text=text,
            option1=opts[0],
            option2=opts[1],
            option3=opts[2],
            option4=opts[3],
            formula=item.get("formula", ""),
            correct_answer=item["correct_answer"]
        )
        await db.add(q)
        inserted += 1
        print(f"Inserted: {text}")

    print(f"Seeding complete. {inserted} new question(s) added.")


if __name__ == "__main__":
    asyncio.run(seed_math_questions())
'''
import asyncio
from utils import DatabaseService1
from utils.db_api.models import Question, Subject
import pandas as pd
# Bu yerga o‘zingiz tuzgan matematika savollari JSON ro‘yxatini joylang
MATH_TESTS = [
    {
        "question": "Quyidagi tenglamani yeching",
        "formula": "0.7\\cdot(6y-5) = 0.4\\cdot(y-3) - 1.16",
        "options": ["0.3", "-3", "-0.3", "2"],
        "correct_answer": "0.3"
    },
    {
        "question": "Quyidagi tenglamani yeching",
        "formula": "0.9\\cdot(4x-2) = 0.5\\cdot(3x-4) + 4.4",
        "options": ["1.2", "2.5", "-3", "2"],
        "correct_answer": "2"
    },
    {
        "question": "Quyidagi tenglamani yeching",
        "formula": "0.2\\cdot(5y-2) = 0.3\\cdot(2y-1) - 0.9",
        "options": ["2", "0.2", "-2", "-1.2"],
        "correct_answer": "-2"
    },
    {
        "question": "Quyidagi tenglamani yeching",
        "formula": "2.8x - 3\\cdot(2x-1) = 2.8 - 3.19x",
        "options": ["-20", "20", "-2", "200"],
        "correct_answer": "20"
    },
    {
        "question": "Quyidagi tenglamani yeching",
        "formula": "5.6 - 7\\cdot(0.8x+1) = 14 - 5.32x",
        "options": ["5.5", "55", "-55", "-5.5"],
        "correct_answer": "-55"
    },
    {
        "question": "Quyidagi tenglamani yeching",
        "formula": "4.5 - 1.6\\cdot(5x-3) = 1.2\\cdot(4x-1) - 15.1",
        "options": ["20", "2", "0.2", "0.5"],
        "correct_answer": "2"
    },
    {
        "question": "Quyidagi tenglamani yeching",
        "formula": "\\frac{6,9}{4,6} = \\frac{x}{5,4}",
        "options": ["7,1", "7,7", "8,4", "9,2"],
        "correct_answer": "7,7"
    },
    {
        "question": "Quyidagi tenglamani yeching",
        "formula": "\\frac{3,5}{x} = \\frac{0,8}{2,4}",
        "options": ["10,5", "13,5", "7,8", "11,5"],
        "correct_answer": "10,5"
    },
    {
        "question": "Quyidagi tenglamani yeching",
        "formula": "\\frac{5,4}{2,4} = \\frac{x}{1,6}",
        "options": ["3,6", "2,8", "4,6", "3,9"],
        "correct_answer": "3,6"
    },
    {
        "question": "Quyidagi tenglamani yeching",
        "formula": "\\frac{0,25}{1,4} = \\frac{0,75}{x}",
        "options": ["3,6", "2,4", "4,2", "5,2"],
        "correct_answer": "4,2"
    },
]


async def seed_math_questions(file_path="questions_export_124.06.2025.xlsx"):
    db = DatabaseService1()
    # await db.add(Subject(name="Nemis tili", subject_val='14', language="O'zbek tili"))
    # await db.add(Subject(name="Fransuz tili", subject_val='15', language="Rus tili"))
    questions = await db.get(Question)
    data = []
    for q in questions:
        data.append({
            "subject_id": q.subject_id,
            "text": q.text,
            "option1": q.option1,
            "option2": q.option2,
            "option3": q.option3,
            "option4": q.option4,
            "correct_answer": q.correct_answer,
            "formula": q.formula or ""
        })

    df = pd.DataFrame(data)
    df.to_excel(file_path, index=False)
    print(f"✅ Savollar saqlandi: {file_path}")


if __name__ == "__main__":
    asyncio.run(seed_math_questions())
'''
