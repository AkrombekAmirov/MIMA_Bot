# test.py
import asyncio
from utils import DatabaseService1
from utils.db_api.models import Subject, Question
from json import loads

# Bu yerga o‘zingiz tuzgan matematika savollari JSON ro‘yxatini joylang
MATH_TESTS = [
  {
    "question": "Quyidagini soddalashtiring",
    "formula": "\\frac{2x + 4}{2}",
    "options": ["x + 1", "x + 2", "x + 4", "2x + 2"],
    "correct_answer": "x + 2"
  },
  {
    "question": "Ildiz ifodani soddalashtiring",
    "formula": "\\sqrt{81x^2}",
    "options": ["9x", "81x", "x", "x^2"],
    "correct_answer": "9x"
  },
  {
    "question": "To‘g‘ri burchakli uchburchakning bitta burchagi 35°. Ikkinchisi nechaga teng?",
    "formula": "",
    "options": ["55°", "65°", "45°", "75°"],
    "correct_answer": "55°"
  },
  {
    "question": "Masshtabi 1:500 bo‘lgan xaritada 2 sm – haqiqiy hayotda necha metrga teng?",
    "formula": "",
    "options": ["10", "50", "100", "500"],
    "correct_answer": "10"
  },
  {
    "question": "Soddalashtiring",
    "formula": "(x + 3)^2",
    "options": ["x^2 + 6x + 9", "x^2 + 3x + 9", "x^2 + 9", "x^2 + 6x"],
    "correct_answer": "x^2 + 6x + 9"
  },
  {
    "question": "Sonlar ketma-ketligi: 2, 4, 8, 16, ... Keyingi son?",
    "formula": "",
    "options": ["24", "26", "30", "32"],
    "correct_answer": "32"
  },
  {
    "question": "Kasr ustida amal bajaring",
    "formula": "\\frac{3}{4} + \\frac{5}{8}",
    "options": ["\\frac{7}{8}", "\\frac{1}{2}", "\\frac{11}{8}", "\\frac{1}{4}"],
    "correct_answer": "\\frac{11}{8}"
  },
  {
    "question": "To‘g‘ri chiziqli tenglama ko‘rinishi qaysi?",
    "formula": "",
    "options": ["y = 2x + 3", "y = x^2", "x^2 + y^2 = 1", "y = \\sqrt{x}"],
    "correct_answer": "y = 2x + 3"
  },
  {
    "question": "Parabola grafigi qaysi ifoda bilan ifodalanadi?",
    "formula": "",
    "options": ["y = x^2", "y = x", "y = \\sqrt{x}", "y = \\frac{1}{x}"],
    "correct_answer": "y = x^2"
  },
  {
    "question": "Pifagor teoremasi qaysi ifoda bilan berilgan?",
    "formula": "",
    "options": ["a^2 + b^2 = c^2", "a + b = c", "a^2 = b^2 + c", "a^2 - b^2 = c"],
    "correct_answer": "a^2 + b^2 = c^2"
  },
  {
    "question": "Sonni foizga aylantiring: 0.75",
    "formula": "",
    "options": ["25%", "50%", "75%", "100%"],
    "correct_answer": "75%"
  },
  {
    "question": "10 ning 3-darajasi nechaga teng?",
    "formula": "10^3",
    "options": ["30", "100", "1000", "10000"],
    "correct_answer": "1000"
  },
  {
    "question": "Tenglamani yeching",
    "formula": "5x = 20",
    "options": ["2", "4", "5", "6"],
    "correct_answer": "4"
  },
  {
    "question": "Kasrni foiz ko‘rinishga o‘tkazing: ",
    "formula": "\\frac{1}{5}",
    "options": ["5%", "10%", "20%", "25%"],
    "correct_answer": "20%"
  },
  {
    "question": "Bo‘linmani hisoblang",
    "formula": "45 \\div 5",
    "options": ["7", "8", "9", "10"],
    "correct_answer": "9"
  },
  {
    "question": "Quyidagi ifodani soddalashtiring: ",
    "formula": "x^2 - 4",
    "options": ["(x - 2)^2", "(x + 2)(x - 2)", "x(x - 4)", "x^2"],
    "correct_answer": "(x + 2)(x - 2)"
  },
  {
    "question": "Sinus va kosinus orasidagi asosiy formulani tanlang",
    "formula": "",
    "options": ["\\sin^2 x + \\cos^2 x = 1", "\\sin x + \\cos x = 1", "\\tan x = \\sin x \\cos x", "\\cos^2 x - \\sin^2 x = 1"],
    "correct_answer": "\\sin^2 x + \\cos^2 x = 1"
  },
  {
    "question": "a = 5 va b = 2 bo‘lsa, Quyidagi ifodani hisoblang",
    "formula": "(a - b)^2",
    "options": ["9", "25", "12", "8"],
    "correct_answer": "9"
  },
  {
    "question": "Logarifm asosini toping:",
    "formula": "\\log_3 81 = x",
    "options": ["2", "3", "4", "5"],
    "correct_answer": "4"
  },
  {
    "question": "Raqamli ifodani hisoblang: ",
    "formula": "2^5",
    "options": ["32", "16", "64", "48"],
    "correct_answer": "32"
  },
  {
    "question": "Chiziqli tenglama: y = 2x + 3. x = -1 bo‘lsa, y nechi?",
    "formula": "",
    "options": ["1", "2", "0", "-1"],
    "correct_answer": "1"
  },
  {
    "question": "a = 3, b = 2. Quyidagi ifodani hisoblang.",
    "formula": "ab + a^2",
    "options": ["9", "15", "12", "18"],
    "correct_answer": "15"
  },
  {
    "question": "a = -2, b = 5. Quyidagi ifodani hisoblang.",
    "formula": "(a - b)^2",
    "options": ["49", "9", "36", "16"],
    "correct_answer": "49"
  },
  {
    "question": "Raqamli ifodani toping: ",
    "formula": "0.2 \\times 0.5",
    "options": ["0.01", "0.05", "0.1", "0.25"],
    "correct_answer": "0.1"
  },
  {
    "question": "Tangens 45° qiymatini toping",
    "formula": "\\tan 45^\\circ",
    "options": ["0", "1", "\\frac{1}{2}", "\\sqrt{2}"],
    "correct_answer": "1"
  },
  {
    "question": "Eksponentaning qiymati nechaga teng?",
    "formula": "e^0",
    "options": ["0", "1", "e", "10"],
    "correct_answer": "1"
  },
  {
    "question": "5 ning kvadrati nechaga teng?",
    "formula": "5^2",
    "options": ["10", "15", "20", "25"],
    "correct_answer": "25"
  },
  {
    "question": "Ildizdan chiqaring: ",
    "formula": "\\sqrt{121}",
    "options": ["10", "11", "12", "13"],
    "correct_answer": "11"
  },
  {
    "question": "Kasrni soddalashtiring: ",
    "formula": "\\frac{18}{24}",
    "options": ["\\frac{3}{4}", "\\frac{2}{3}", "\\frac{4}{5}", "\\frac{5}{6}"],
    "correct_answer": "\\frac{3}{4}"
  },
  {
    "question": "x = 4 bo‘lsa, Quyidagi algebraik ifodani hisoblang",
    "formula": "x^2 - 2x",
    "options": ["8", "10", "12", "16"],
    "correct_answer": "8"
  },
  {
    "question": "To‘g‘ri burchakli uchburchak: katet = 5 va 12. Gipotenuzani toping.",
    "formula": "\\sqrt{5^2 + 12^2}",
    "options": ["11", "12", "13", "14"],
    "correct_answer": "13"
  },
  {
    "question": "100 sonining 15 foizi nechaga teng?",
    "formula": "",
    "options": ["10", "15", "20", "25"],
    "correct_answer": "15"
  },
  {
    "question": "Quyidagi algebraik ifoda ni oching.",
    "formula": "x(x + 2)",
    "options": ["x^2 + 2", "x + 2x", "x^2 + 2x", "2x^2"],
    "correct_answer": "x^2 + 2x"
  },
  {
    "question": "Qarshi sonini toping: qarshi soni \\( -5 \\) ga teng bo‘lgan son?",
    "formula": "",
    "options": ["-5", "0", "5", "-10"],
    "correct_answer": "5"
  },
  {
    "question": "Kvadrat ildiz ichidagi ifodani soddalashtiring:",
    "formula": "\\sqrt{36a^2}",
    "options": ["6a", "36a", "a^2", "12a"],
    "correct_answer": "6a"
  },
  {
    "question": "Tangens formulasini tanlang",
    "formula": "",
    "options": ["\\tan x = \\frac{\\sin x}{\\cos x}", "\\tan x = \\sin x \\cos x", "\\tan x = \\frac{1}{\\cos x}", "\\tan x = \\cos x \\sin x"],
    "correct_answer": "\\tan x = \\frac{\\sin x}{\\cos x}"
  },
  {
    "question": "Qaysi son tub son emas?",
    "formula": "",
    "options": ["2", "3", "4", "5"],
    "correct_answer": "4"
  }
]


async def seed_math_questions():
    db = DatabaseService1()
    # 1) Matematika (O‘zbek tilida) subjectini aniqlaymiz
    # subs = await db.get(Subject, filters={"name": "Matematika", "language": "O'zbek"})
    # if not subs:
    #     print("Error: 'Matematika' subject topilmadi.")
    #     return
    # subject = subs[0]
    # subject_id = subject.id

    inserted = 0
    for item in MATH_TESTS:
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
            subject_id=2,
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
