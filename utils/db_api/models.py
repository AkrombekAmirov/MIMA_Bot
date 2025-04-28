from sqlmodel import SQLModel, Field, Column, TEXT, Relationship
from typing import Optional, Dict, List
from datetime import datetime
from json import loads, dumps
from pytz import timezone


class BaseModel(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_date: str = Field(default_factory=lambda: datetime.now(timezone('Asia/Tashkent')).strftime("%d:%m:%y"),
                              description="Yaratilgan vaqt")
    created_time: str = Field(default_factory=lambda: datetime.now(timezone('Asia/Tashkent')).strftime("%H:%M:%S"),
                              description="Yaratilgan vaqt")
    updated_date: Optional[str] = Field(default=None, description="Yangilangan sana")
    updated_time: Optional[str] = Field(default=None, description="Yangilangan vaqt")

    def to_dict(self) -> dict:
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}


class User(SQLModel, table=True):
    """🔥 Eng xavfsiz foydalanuvchi modeli 🔥"""

    id: Optional[int] = Field(default=None, primary_key=True)
    username: Optional[str] = Field(default=None, index=True)
    telegram_id: str = Field(unique=True, index=True)
    phone_number: Optional[str] = Field(default=None, max_length=12, nullable=True)  # 🔒 Shifrlangan holda saqlanadi
    telegram_number: str = Field(max_length=12)
    telegram_name: str = Field(max_length=250)
    name: str = Field(max_length=100, nullable=True)

    # Birinchi create paytida bo'sh qoldirilishi mumkin bo'lgan maydonlar
    tuman: str = Field(default="", max_length=100)  # Default bo'sh string
    viloyat: str = Field(default="", max_length=100)
    passport: Optional[str] = Field(default="", max_length=9)  # None bo'lsa keyinchalik update qilinadi
    faculty: str = Field(default="", max_length=100)
    talim_turi: str = Field(default="", max_length=50)
    talim_tili: str = Field(default="", max_length=50)
    jshir_id: str = Field(default="", max_length=13, nullable=True)
    test_point: str = Field(default="", max_length=3)
    status: bool = Field(default=False, description="Abituryent holati")

    created_date: str
    created_time: str

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Hozirgi vaqtdagi o'zgaruvchilarni o'rnatamiz
        now = datetime.now(timezone('Asia/Tashkent'))
        self.created_date = now.strftime("%Y-%m-%d")
        self.created_time = now.strftime("%H:%M:%S")


class Subject(BaseModel, table=True):
    __tablename__ = 'subjects'
    name: str = Field(..., description="Fan nomi")
    subject_val: str = Field(..., description="Fan qiymati")


class Faculty(BaseModel, table=True):
    __tablename__ = 'faculties'
    name: str = Field(..., description="Fakultet nomi")
    faculty_val: str = Field(..., description="Fakultet qiymati")

    blocks: List["FacultyBlock"] = Relationship(back_populates="faculty")


class FacultyBlock(SQLModel, table=True):
    __tablename__ = 'faculty_blocks'

    id: Optional[int] = Field(default=None, primary_key=True)
    faculty_id: int = Field(foreign_key="faculties.id")
    subject_id: int = Field(foreign_key="subjects.id")
    block_number: int = Field(..., description="Blok raqami: 1, 2 yoki 3")

    faculty: Faculty = Relationship(back_populates="blocks")
    subject: Subject = Relationship()


class Question(BaseModel, table=True):
    __tablename__ = 'questions'
    subject_id: int = Field(..., description="Fan ID")
    text: str = Field(..., description="Savol matni")
    option1: str = Field(..., description="Javob variantlari")
    option2: str = Field(..., description="Javob variantlari")
    option3: str = Field(..., description="Javob variantlari")
    option4: str = Field(..., description="Javob variantlari")
    correct_answer: str = Field(..., description="To'g'ri javob")

    def get_options(self) -> Dict[str, str]:
        return loads(self.options) if self.options else {}


class Result(BaseModel, table=True):
    __tablename__ = 'results'
    user_id: str = Field(sa_column=Column(TEXT), description="Foydalanuvchi ID")
    subject_id: int = Field(..., description="Fan ID")
    question_ids: str = Field(sa_column=Column(TEXT), description="Savol ID larining ro'yxati JSON formatida")
    user_answers: str = Field(sa_column=Column(TEXT), description="Foydalanuvchi javoblari JSON formatida")
    correct_answers: int = Field(default=0, description="To'g'ri javoblar soni")
    wrong_answers: int = Field(default=0, description="Noto'g'ri javoblar soni")
    number: int = Field(default=0, description="Test holati uchun")
    status: bool = Field(default=False, description="Test holati")

    class Config:
        from_attributes = True
        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}

    def set_question_ids(self, ids: List[int]) -> None:
        """Savol ID larini JSON formatida saqlaydi."""
        self.question_ids = dumps(ids)

    def get_question_ids(self) -> List[int]:
        """Savol ID larini JSON formatidan ro‘yxatga aylantiradi."""
        return loads(self.question_ids) if self.question_ids else []

    def set_user_answers(self, answers: List[str]) -> None:
        """Foydalanuvchi javoblarini JSON formatida saqlaydi."""
        self.user_answers = dumps(answers)

    def get_user_answers(self) -> List[str]:
        """Foydalanuvchi javoblarini JSON formatidan ro‘yxatga aylantiradi."""
        return loads(self.user_answers) if self.user_answers else []

    def add_user_answer(self, question_id: int, answer: str) -> None:
        """
        Foydalanuvchi tomonidan berilgan javobni qo'shadi.
        Savolga javob qo'shish uchun, user_answers listiga yangi javobni kiritadi.
        """
        # Savol ID larini olish
        question_ids = self.get_question_ids()

        # Foydalanuvchi javoblarini olish
        user_answers = self.get_user_answers()

        # Agar savol ID mavjud bo'lsa, uni yangilaymiz
        if question_id not in question_ids:
            question_ids.append(question_id)
            user_answers.append(answer)
        else:
            # Agar savol allaqachon kiritilgan bo'lsa, javobni yangilaymiz
            index = question_ids.index(question_id)
            user_answers[index] = answer

        # Yangilangan ma'lumotlarni saqlaymiz
        self.set_question_ids(question_ids)
        self.set_user_answers(user_answers)

    def update_score(self, correct: int, wrong: int) -> None:
        """Natijalarni yangilaydi."""
        self.correct_answers += correct
        self.wrong_answers += wrong

    def accuracy(self) -> float:
        """To‘g‘ri javoblar foizini qaytaradi."""
        total_answers = self.correct_answers + self.wrong_answers
        return (self.correct_answers / total_answers) * 100 if total_answers > 0 else 0

    def is_passed(self) -> bool:
        """Testdan o‘tish holatini tekshiradi."""
        return self.accuracy() >= 50

    def to_summary(self) -> dict:
        """Natijalar haqida qisqacha ma'lumot."""
        return {
            "user_id": self.user_id,
            "test_id": self.id,
            "accuracy": self.accuracy(),
            "status": self.status,
            "created_date": self.created_date.isoformat()
        }
