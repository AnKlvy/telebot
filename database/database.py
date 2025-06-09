"""
Конфигурация подключения к базе данных
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from os import getenv
from dotenv import load_dotenv
from .models import Base

load_dotenv()

# Формируем DATABASE_URL из отдельных переменных для избежания дублирования
POSTGRES_USER = getenv("POSTGRES_USER", "telebot_user")
POSTGRES_PASSWORD = getenv("POSTGRES_PASSWORD", "your_secure_password")
POSTGRES_DB = getenv("POSTGRES_DB", "telebot")
POSTGRES_HOST = getenv("POSTGRES_HOST", "postgres")
POSTGRES_PORT = getenv("POSTGRES_PORT", "5432")

DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# Создание движка и сессии
engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# Функции инициализации базы данных
async def init_database():
    """Инициализация базы данных - создание всех таблиц"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ База данных инициализирована")


async def close_database():
    """Закрытие соединения с базой данных"""
    await engine.dispose()
    print("🔌 Соединение с базой данных закрыто")


# Функция для получения сессии базы данных
def get_db_session() -> AsyncSession:
    """Получить сессию базы данных"""
    return async_session()
