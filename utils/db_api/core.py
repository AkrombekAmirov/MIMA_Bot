from sqlmodel import Session, select
from typing import Optional
from .models import User


class DatabaseService:
    def __init__(self, engine):
        self.engine = engine

    def __add_or_update(self, session: Session, user: User, user_data: dict):
        """Foydalanuvchi mavjud bo'lsa, update qiladi, aks holda yaratadi."""
        if user:  # Foydalanuvchi mavjud bo'lsa, ma'lumotlarni yangilash
            for key, value in user_data.items():
                if hasattr(user, key) and value is not None:  # Faqat bo'sh bo'lmagan qiymatlarni yangilash
                    setattr(user, key, value)
        else:  # Yangi foydalanuvchi yaratish
            user = User(**user_data)
            session.add(user)

        session.commit()
        session.refresh(user)
        print(f"User added/updated: {user}")
        return user.id

    def add_user(self, telegram_id: str, username: Optional[str] = None, phone_number: Optional[str] = None,
                 telegram_number: Optional[str] = None, telegram_name: Optional[str] = None, name: Optional[str] = None,
                 tuman: Optional[str] = None, viloyat: Optional[str] = None,
                 passport: Optional[str] = None, faculty: Optional[str] = None,
                 talim_turi: Optional[str] = None, talim_tili: Optional[str] = None, jshir_id: Optional[str] = None):
        """Foydalanuvchini qo'shadi yoki yangilaydi."""
        with Session(self.engine) as session:
            # Telegram ID bo‘yicha foydalanuvchini qidirish
            user = session.exec(select(User).where(User.telegram_id == telegram_id)).first()

            user_data = {
                "username": username,
                "telegram_id": telegram_id,
                "phone_number": phone_number,
                "telegram_number": telegram_number,
                "telegram_name": telegram_name,
                "name": name,
                "tuman": tuman,
                "viloyat": viloyat,
                "passport": passport,
                "jshir_id": jshir_id,
                "faculty": faculty,
                "talim_turi": talim_turi,
                "talim_tili": talim_tili
            }

            return self.__add_or_update(session, user, user_data)

    def get_user_exists(self, telegram_id: str) -> bool:
        """Foydalanuvchi mavjudligini tekshiradi."""
        with Session(self.engine) as session:
            return session.exec(select(User).where(User.telegram_id == telegram_id)).first() is not None

    def get_by_passport_exists(self, passport: str) -> bool:
        """Foydalanuvchi passport mavjudligini tekshiradi."""
        with Session(self.engine) as session:
            return session.exec(select(User).where(User.passport == passport)).first() is not None

    def get_by_telegram_id(self, telegram_id: str) -> User:
        with Session(self.engine) as session:
            return session.exec(select(User).where(User.telegram_id == telegram_id)).first()
