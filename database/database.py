"""
Конфигурация подключения к базе данных
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
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

    # Выполняем миграцию кураторов и групп
    await migrate_curator_groups()

    print("✅ База данных инициализирована")


async def close_database():
    """Закрытие соединения с базой данных"""
    await engine.dispose()
    print("🔌 Соединение с базой данных закрыто")


async def migrate_curator_groups():
    """Миграция данных кураторов и групп от One-to-One к Many-to-Many"""
    async with async_session() as session:
        try:
            # Проверяем, существует ли старое поле group_id
            result = await session.execute(text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'curators' AND column_name = 'group_id'
            """))

            if not result.fetchone():
                # Миграция уже выполнена
                return

            print("🔄 Выполняем миграцию связей кураторов и групп...")

            # Получаем данные из старого поля group_id
            result = await session.execute(
                text("SELECT id, group_id FROM curators WHERE group_id IS NOT NULL")
            )
            curator_group_pairs = result.fetchall()

            # Переносим данные в таблицу связи Many-to-Many
            for curator_id, group_id in curator_group_pairs:
                # Проверяем, не существует ли уже такая связь
                existing = await session.execute(
                    text("SELECT 1 FROM curator_groups WHERE curator_id = :curator_id AND group_id = :group_id"),
                    {"curator_id": curator_id, "group_id": group_id}
                )

                if not existing.fetchone():
                    await session.execute(
                        text("INSERT INTO curator_groups (curator_id, group_id) VALUES (:curator_id, :group_id)"),
                        {"curator_id": curator_id, "group_id": group_id}
                    )

            # Удаляем старое поле group_id
            await session.execute(text("ALTER TABLE curators DROP COLUMN group_id"))
            await session.commit()

            print(f"✅ Миграция завершена: перенесено {len(curator_group_pairs)} связей")

        except Exception as e:
            await session.rollback()
            print(f"⚠️ Миграция пропущена или завершена с ошибкой: {e}")


# Функция для получения сессии базы данных
def get_db_session() -> AsyncSession:
    """Получить сессию базы данных"""
    return async_session()
