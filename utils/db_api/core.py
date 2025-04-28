from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from tenacity import retry, wait_exponential, stop_after_attempt
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import Session, select, SQLModel, and_
from .models import User, Subject, Result, Question
from typing import Optional, List, Type, Dict, Any
from contextlib import asynccontextmanager
from LoggingService import LoggerService
from sqlalchemy.orm import sessionmaker
from data import DATABASE_URL
from time import time


class DatabaseService1:
    """PostgreSQL uchun rivojlangan asinxron ma'lumotlar bazasi xizmati."""
    MAX_RETRIES = 5
    ENGINE: Optional[AsyncEngine] = None

    def __init__(self, logger: Optional[LoggerService] = None):
        self.engine = self.get_engine()
        self.logging = logger.get_logger() if logger else None
        self.session_factory = sessionmaker(bind=self.engine, class_=AsyncSession, expire_on_commit=False)

    @classmethod
    def get_engine(cls) -> AsyncEngine:
        """Havza ulanishi sozlanadi."""
        if cls.ENGINE is None:
            cls.ENGINE = create_async_engine(
                DATABASE_URL,
                echo=False,
                pool_size=50,  # Increased pool size for higher concurrency
                max_overflow=25,  # Increased max overflow
                pool_timeout=30,  # Reduced pool timeout
                pool_recycle=300,  # Connection recycle time (5 minutes)
                pool_pre_ping=True,  # Enable connection health checks
                connect_args={
                    "server_settings": {
                        "application_name": "DarsJadval",
                        "statement_timeout": "60000",  # 60 seconds timeout for queries
                        "idle_in_transaction_session_timeout": "300000",  # 5 minutes timeout for idle transactions
                    }
                }
            )
        return cls.ENGINE

    @asynccontextmanager
    async def session_scope(self):
        """Sessiyani avtomatik boshqarish uchun kontekst menejeri."""
        async with self.get_session() as session:
            try:
                yield session
            except Exception as e:
                if self.logging:
                    self.logging.error(f"Session error: {e}", exc_info=True)
                await session.rollback()
                raise
            finally:
                await session.close()

    def get_session(self) -> AsyncSession:
        """Yangi sessiya ob'ektini qaytaradi."""
        return self.session_factory()

    @retry(wait=wait_exponential(multiplier=1, min=1, max=10), stop=stop_after_attempt(MAX_RETRIES))
    async def execute_query(self, query: Any, *args, **kwargs):
        """Umumiy so'rovni bajaruvchi funksiya."""
        start_time = time()
        async with self.session_scope() as session:
            try:
                if self.logging:
                    self.logging.info(f"Executing query: {query.__name__ if callable(query) else query}")
                result = await query(session, *args, **kwargs) if callable(query) else await session.execute(query)
                elapsed_time = time() - start_time
                if self.logging:
                    self.logging.info(f"Query executed in {elapsed_time:.2f} seconds.")
                return result
            except Exception as e:
                if self.logging:
                    self.logging.error(f"Error executing query: {e}", exc_info=True)
                raise

    async def add(self, instance: SQLModel) -> Optional[int]:
        """Yangi yozuv qo'shadi."""
        async with self.session_scope() as session:
            try:
                session.add(instance)
                await session.commit()
                await session.refresh(instance)
                if self.logging:
                    self.logging.info(f"Added instance: {instance}")
                return instance.id
            except Exception as e:
                if self.logging:
                    self.logging.error(f"Error adding instance: {e}", exc_info=True)
                raise

    async def update(self, instance: SQLModel) -> Optional[int]:
        """Mavjud yozuvni yangilaydi."""
        async with self.session_scope() as session:
            try:
                instance = await session.merge(instance)
                await session.commit()
                await session.refresh(instance)
                if self.logging:
                    self.logging.info(f"Updated instance: {instance}")
                return instance.id
            except Exception as e:
                if self.logging:
                    self.logging.error(f"Error updating instance: {e}", exc_info=True)
                raise

    async def update_user_by_telegram_id(self, telegram_id: str, updates: dict):
        """Telegram ID orqali foydalanuvchini yangilaydi."""
        async with AsyncSession(self.engine) as session:
            # Telegram ID orqali foydalanuvchini topamiz
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()

            if user:
                # Dikt orqali yangilanishlarni qo‘llash
                for key, value in updates.items():
                    if value is not None:
                        setattr(user, key, value)

                # Yangilangan foydalanuvchini saqlaymiz
                return await self.update(user)
            else:
                self.logging.error(f"User with telegram_id {telegram_id} not found")
                return None

    async def get(self, model: Type[SQLModel], filters: Optional[Dict[str, Any]] = None, limit: Optional[int] = None) -> \
            List[SQLModel]:
        """
        Jadvaldan yozuvlarni olish.
        :param model: SQLModel jadvali turi.
        :param filters: Filtlash shartlari (masalan, {"id": 1}).
        :param limit: Qaytariladigan yozuvlar soni.
        :return: Model yozuvlari.
        """
        async with self.session_scope() as session:
            try:
                query = select(model)
                if filters:
                    conditions = [getattr(model, key) == value for key, value in filters.items() if hasattr(model, key)]
                    if conditions:
                        query = query.where(and_(*conditions))
                    elif self.logging:
                        self.logging.warning(f"No valid filters applied for model {model.__name__}")

                if limit:
                    query = query.limit(limit)

                result = await session.execute(query)
                records = result.scalars().all()
                if self.logging:
                    self.logging.info(f"Retrieved {len(records)} records from {model.__name__}")
                return records
            except Exception as e:
                if self.logging:
                    self.logging.error(f"Error retrieving data from {model.__name__}: {e}", exc_info=True)
                raise


async def get_db_core() -> DatabaseService1:
    return DatabaseService1()

#
# class DatabaseService:
#     def __init__(self, engine):
#         self.engine = engine
#
#     def __add_or_update(self, session: Session, user: User, user_data: dict):
#         """Foydalanuvchi mavjud bo'lsa, update qiladi, aks holda yaratadi."""
#         if user:  # Foydalanuvchi mavjud bo'lsa, ma'lumotlarni yangilash
#             for key, value in user_data.items():
#                 if hasattr(user, key) and value is not None:  # Faqat bo'sh bo'lmagan qiymatlarni yangilash
#                     setattr(user, key, value)
#         else:  # Yangi foydalanuvchi yaratish
#             user = User(**user_data)
#             session.add(user)
#
#         session.commit()
#         session.refresh(user)
#         print(f"User added/updated: {user}")
#         return user.id
#
#     def add_user(self, telegram_id: str, username: Optional[str] = None, phone_number: Optional[str] = None,
#                  telegram_number: Optional[str] = None, telegram_name: Optional[str] = None, name: Optional[str] = None,
#                  tuman: Optional[str] = None, viloyat: Optional[str] = None,
#                  passport: Optional[str] = None, faculty: Optional[str] = None,
#                  talim_turi: Optional[str] = None, talim_tili: Optional[str] = None, jshir_id: Optional[str] = None):
#         """Foydalanuvchini qo'shadi yoki yangilaydi."""
#         with Session(self.engine) as session:
#             # Telegram ID bo‘yicha foydalanuvchini qidirish
#             user = session.exec(select(User).where(User.telegram_id == telegram_id)).first()
#
#             user_data = {
#                 "username": username,
#                 "telegram_id": telegram_id,
#                 "phone_number": phone_number,
#                 "telegram_number": telegram_number,
#                 "telegram_name": telegram_name,
#                 "name": name,
#                 "tuman": tuman,
#                 "viloyat": viloyat,
#                 "passport": passport,
#                 "jshir_id": jshir_id,
#                 "faculty": faculty,
#                 "talim_turi": talim_turi,
#                 "talim_tili": talim_tili
#             }
#
#             return self.__add_or_update(session, user, user_data)
#
#     def get_user_exists(self, telegram_id: str) -> bool:
#         """Foydalanuvchi mavjudligini tekshiradi."""
#         with Session(self.engine) as session:
#             return session.exec(select(User).where(User.telegram_id == telegram_id)).first() is not None
#
#     def get_by_passport_exists(self, passport: str) -> bool:
#         """Foydalanuvchi passport mavjudligini tekshiradi."""
#         with Session(self.engine) as session:
#             return session.exec(select(User).where(User.passport == passport)).first() is not None
#
#     def get_by_telegram_id(self, telegram_id: str) -> User:
#         with Session(self.engine) as session:
#             return session.exec(select(User).where(User.telegram_id == telegram_id)).first()
