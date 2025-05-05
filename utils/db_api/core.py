from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from .models import User, Subject, Result, Question, Faculty, FacultyBlock, UserAnswer
from sqlalchemy.exc import DBAPIError, OperationalError, InterfaceError
from typing import Optional, List, Type, Dict, Any, Callable, Coroutine
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import Session, select, SQLModel, and_
from asyncpg.exceptions import PostgresError
from contextlib import asynccontextmanager
from LoggingService import LoggerService
from sqlalchemy.orm import sessionmaker
from data import DATABASE_URL
from time import time


class DatabaseService1:
    """PostgreSQL uchun mustahkam, xavfsiz va yuqori darajadagi asinxron ma'lumotlar bazasi xizmati."""
    MAX_RETRIES = 5
    ENGINE: Optional[AsyncEngine] = None

    def __init__(self, logger: Optional[LoggerService] = None):
        self.engine = self.get_engine()
        self.logging = logger.get_logger() if logger else None
        self.session_factory = sessionmaker(bind=self.engine, class_=AsyncSession, expire_on_commit=False)

    @classmethod
    def get_engine(cls) -> AsyncEngine:
        if cls.ENGINE is None:
            cls.ENGINE = create_async_engine(
                DATABASE_URL,
                echo=False,
                pool_size=50,
                max_overflow=25,
                pool_timeout=30,
                pool_recycle=1800,  # 30 daqiqa
                pool_pre_ping=True,
                connect_args={
                    "server_settings": {
                        "application_name": "DarsJadval",
                        "statement_timeout": "60000",
                        "idle_in_transaction_session_timeout": "300000",
                    }
                }
            )
        return cls.ENGINE

    @asynccontextmanager
    async def session_scope(self):
        session = self.get_session()
        try:
            yield session
            await session.commit()
        except (DBAPIError, OperationalError, InterfaceError, PostgresError) as db_err:
            if self.logging:
                self.logging.error("Database error during session_scope", exc_info=True)
            await session.rollback()
            raise
        except Exception as e:
            if self.logging:
                self.logging.error("General error during session_scope", exc_info=True)
            await session.rollback()
            raise
        finally:
            try:
                await session.close()
            except Exception as e:
                if self.logging:
                    self.logging.warning("Session close failed", exc_info=True)

    def get_session(self) -> AsyncSession:
        return self.session_factory()

    @retry(
        wait=wait_exponential(multiplier=1, min=1, max=10),
        stop=stop_after_attempt(MAX_RETRIES),
        retry=retry_if_exception_type((DBAPIError, OperationalError, InterfaceError, PostgresError))
    )
    async def execute_query(self, query: Callable[[AsyncSession], Coroutine], *args, **kwargs):
        start_time = time()
        async with self.session_scope() as session:
            try:
                if self.logging:
                    self.logging.info(f"Executing query: {getattr(query, '__name__', str(query))}")
                result = await query(session, *args, **kwargs)
                elapsed_time = time() - start_time
                if self.logging:
                    self.logging.info(f"Query executed in {elapsed_time:.2f} seconds.")
                return result
            except (DBAPIError, OperationalError, InterfaceError, PostgresError) as db_err:
                if self.logging:
                    self.logging.error("Database-level error in execute_query", exc_info=True)
                raise
            except Exception as e:
                if self.logging:
                    self.logging.error("General error in execute_query", exc_info=True)
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

    async def update_by_field(self, model: Type[SQLModel], field_name: str, field_value: Any, updates: dict) -> \
            Optional[int]:
        """
        Model va field_name orqali yozuvni yangilaydi.
        :param model: Yangilanishi kerak bo‘lgan model (masalan: User, Subject, va h.k.)
        :param field_name: Yozuvni izlash uchun ishlatiladigan maydon nomi (masalan: "telegram_id", "id")
        :param field_value: Yuqoridagi maydonning qiymati (masalan: "123456", 1)
        :param updates: Yangilanishlarni ko‘rsatuvchi dict (masalan, {"username": "new_value"})
        :return: Yangilangan yozuvning ID si yoki None
        """
        async with self.session_scope() as session:
            try:
                # Field orqali yozuvni topish
                query = select(model).where(getattr(model, field_name) == field_value)
                result = await session.execute(query)
                instance = result.scalar_one_or_none()

                if instance:
                    # Dikt orqali yangilanishlarni qo‘llash
                    for key, value in updates.items():
                        if value is not None and hasattr(instance, key):
                            setattr(instance, key, value)

                    # Yozuvni yangilash
                    instance = await session.merge(instance)

                    # Yangilanishlarni saqlash
                    await session.commit()

                    # Yangilangan yozuvni qaytarish
                    await session.refresh(instance)

                    if self.logging:
                        self.logging.info(f"Updated {model.__name__} instance with {field_name} = {field_value}")
                    return instance.id
                else:
                    if self.logging:
                        self.logging.error(f"{model.__name__} with {field_name} = {field_value} not found")
                    return None
            except Exception as e:
                if self.logging:
                    self.logging.error(
                        f"Error updating {model.__name__} instance with {field_name} = {field_value}: {e}",
                        exc_info=True)
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


async def get_db_core() -> DatabaseService1:
    return DatabaseService1()
