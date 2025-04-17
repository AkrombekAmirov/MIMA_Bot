from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
from pytz import timezone


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

    created_date: str
    created_time: str

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Hozirgi vaqtdagi o'zgaruvchilarni o'rnatamiz
        now = datetime.now(timezone('Asia/Tashkent'))
        self.created_date = now.strftime("%Y-%m-%d")
        self.created_time = now.strftime("%H:%M:%S")
