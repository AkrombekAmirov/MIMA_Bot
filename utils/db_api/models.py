from sqlmodel import SQLModel, Field, Column, TEXT
from datetime import datetime, date, time
from typing import Optional, Dict, List
from pydantic import root_validator
from json import loads, dumps
from random import shuffle
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
    test_point: str = Field(default="", max_length=3, nullable=True)
    status: bool = Field(default=False, description="Abituryent holati", nullable=True)

    created_date: str
    created_time: str

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Hozirgi vaqtdagi o'zgaruvchilarni o'rnatamiz
        now = datetime.now(timezone('Asia/Tashkent'))
        self.created_date = now.strftime("%Y-%m-%d")
        self.created_time = now.strftime("%H:%M:%S")


class Subject(SQLModel, table=True):
    __tablename__ = 'subjects'
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(..., description="Fan nomi")
    subject_val: str = Field(..., description="Fan qiymati")
    language: str = Field(..., description="Fan tili: (O'zbek, Rus, Ingliz...)")

    # 📌 FAN BO‘YICHA QO‘SHIMCHA METODLAR

    def is_uzbek(self) -> bool:
        """Fan o‘zbek tilidami?"""
        return self.language.lower() in ["o'zbek", "uzbek", "uz"]

    def is_russian(self) -> bool:
        """Fan rus tilidami?"""
        return self.language.lower() in ["rus", "russian", "ru"]

    def is_english(self) -> bool:
        """Fan ingliz tilidami?"""
        return self.language.lower() in ["english", "ingliz", "en"]

    def matches_language(self, lang: str) -> bool:
        """Fan tili kiritilgan til bilan mos keladimi?"""
        return self.language.lower() == lang.lower()

    def to_dict(self) -> dict:
        """Dictionary formatida chiqarish (API uchun qulay)"""
        return {
            "id": self.id,
            "name": self.name,
            "subject_val": self.subject_val,
            "language": self.language,
            "description": self.description,
            "created_date": self.created_date,
            "created_time": self.created_time
        }

    def __repr__(self):
        return f"<Subject: {self.name} [{self.language}]>"


class Faculty(BaseModel, table=True):
    __tablename__ = 'faculties'
    name: str = Field(..., description="Fakultet nomi")
    faculty_val: str = Field(..., description="Fakultet qiymati")
    talim_tili: str = Field(..., description="Fakultet tili")


class FacultyBlock(SQLModel, table=True):
    __tablename__ = 'faculty_blocks'

    id: Optional[int] = Field(default=None, primary_key=True)
    faculty_val: str = Field(..., description="Fakultet qiymati")
    subject_val: str = Field(..., description="Fan qiymati")  # FOREIGN KEY subject_val ga qilingan
    block_number: int = Field(..., description="Blok raqami: 1, 2 yoki 3")


class Question(BaseModel, table=True):
    __tablename__ = 'questions'
    subject_id: int = Field(..., description="Fan ID")
    text: str = Field(..., description="Savol matni")
    option1: str = Field(..., description="Javob variantlari")
    option2: str = Field(..., description="Javob variantlari")
    option3: str = Field(..., description="Javob variantlari")
    option4: str = Field(..., description="Javob variantlari")
    formula: Optional[str] = Field(default="", description="LaTeX formulasi", nullable=True)
    correct_answer: str = Field(..., description="To'g'ri javob")

    def get_options(self) -> Dict[str, str]:
        return loads(self.options) if self.options else {}

    @root_validator(pre=True)
    def ensure_correct_in_options(cls, values):
        opts = [values.get('option1'), values.get('option2'), values.get('option3'), values.get('option4')]
        corr = values.get('correct_answer')
        if corr not in opts:
            raise ValueError(f"correct_answer '{corr}' must be one of the options {opts}")
        return values

    def options_list(self) -> List[str]:
        """Return the list of answer options in order A-D."""
        return [self.option1, self.option2, self.option3, self.option4]

    def shuffled_options(self) -> List[str]:
        """Return a new list of options in randomized order."""
        opts = self.options_list()
        shuffle(opts)
        return opts

    def is_correct(self, answer: str) -> bool:
        """Check if the provided answer matches the correct one."""
        return answer == self.correct_answer

    def to_dict(self, shuffle: bool = False) -> Dict[str, any]:
        """
        Serialize question to dict for API responses.
        If shuffle=True, options will be randomized.
        """
        opts = self.shuffled_options() if shuffle else self.options_list()
        return {
            "id": self.id,
            "subject_id": self.subject_id,
            "text": self.text,
            "formula": self.formula,
            "options": opts,
            # we don’t expose correct_answer in API payload for exam
        }

    def __repr__(self) -> str:
        return f"<Question id={self.id} subject_id={self.subject_id} text={self.text[:30]!r}...>"


class UserAnswer(SQLModel, table=True):
    __tablename__ = "user_answers"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(..., description="Foydalanuvchi ID (str formatda saqlanadi)")
    subject_id: int = Field(..., description="Fan ID")
    question_id: int = Field(..., description="Savol ID")
    selected_option: str = Field(..., description="Tanlangan variant (A, B, C, D)")
    is_correct: Optional[bool] = Field(default=None, description="Javob to‘g‘rimi?")
    answered_at: str = Field(
        default_factory=lambda: datetime.now(timezone("Asia/Tashkent")).strftime("%Y-%m-%d %H:%M:%S"),
        description="Javob berilgan vaqt"
    )


class Result(SQLModel, table=True):
    __tablename__ = 'results'
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(sa_column=Column(TEXT))
    subject_id: int
    question_ids: str = Field(sa_column=Column(TEXT))  # JSON list of question_ids
    user_answers: str = Field(sa_column=Column(TEXT))  # JSON list of selected_options
    correct_answers: int = Field(default=0)
    wrong_answers: int = Field(default=0)
    number: int = Field(default=0)
    status: bool = Field(default=False)
    created_date: date = Field(default_factory=lambda: datetime.now().date())
    created_time: time = Field(default_factory=lambda: datetime.now().time())
    updated_date: date = Field(default_factory=lambda: datetime.now().date())
    updated_time: time = Field(default_factory=lambda: datetime.now().time())

    class Config:
        from_attributes = True
        populate_by_name = True

    def set_question_ids(self, ids: List[int]) -> None:
        self.question_ids = dumps(ids)

    def get_question_ids(self) -> List[int]:
        return loads(self.question_ids) if self.question_ids else []

    def set_user_answers(self, answers: List[str]) -> None:
        self.user_answers = dumps(answers)

    def get_user_answers(self) -> List[str]:
        return loads(self.user_answers) if self.user_answers else []

    def recalculate_scores(self, correct_map: dict[int, str]) -> None:
        """Savollar bo‘yicha to‘g‘ri va noto‘g‘ri javoblarni yangidan hisoblaydi."""
        correct = 0
        wrong = 0
        q_ids = self.get_question_ids()
        u_ans = self.get_user_answers()
        for i, q_id in enumerate(q_ids):
            if i >= len(u_ans):
                continue
            correct_answer = correct_map.get(q_id)
            if correct_answer:
                if u_ans[i] == correct_answer:
                    correct += 1
                else:
                    wrong += 1
        self.correct_answers = correct
        self.wrong_answers = wrong

    def accuracy(self) -> float:
        total = self.correct_answers + self.wrong_answers
        return (self.correct_answers / total * 100) if total > 0 else 0
