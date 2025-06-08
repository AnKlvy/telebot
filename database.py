import asyncio
import asyncpg
from typing import Optional, Dict, List, Any
from os import getenv
from dotenv import load_dotenv

load_dotenv()

# Формируем DATABASE_URL из отдельных переменных для избежания дублирования
POSTGRES_USER = getenv("POSTGRES_USER", "telebot_user")
POSTGRES_PASSWORD = getenv("POSTGRES_PASSWORD", "your_secure_password")
POSTGRES_DB = getenv("POSTGRES_DB", "telebot")
POSTGRES_HOST = getenv("POSTGRES_HOST", "postgres")
POSTGRES_PORT = getenv("POSTGRES_PORT", "5432")

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

class Database:
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
    
    async def connect(self):
        """Создание пула соединений с базой данных"""
        try:
            self.pool = await asyncpg.create_pool(DATABASE_URL)
            print("✅ Подключение к базе данных установлено")
        except Exception as e:
            print(f"❌ Ошибка подключения к базе данных: {e}")
            raise
    
    async def disconnect(self):
        """Закрытие пула соединений"""
        if self.pool:
            await self.pool.close()
            print("🔌 Соединение с базой данных закрыто")
    
    async def execute(self, query: str, *args) -> str:
        """Выполнение запроса без возврата данных"""
        if not self.pool:
            raise RuntimeError("База данных не подключена")
        async with self.pool.acquire() as connection:
            return await connection.execute(query, *args)
    
    async def fetch(self, query: str, *args) -> List[Dict]:
        """Выполнение запроса с возвратом всех строк"""
        if not self.pool:
            raise RuntimeError("База данных не подключена")
        async with self.pool.acquire() as connection:
            rows = await connection.fetch(query, *args)
            return [dict(row) for row in rows]
    
    async def fetchrow(self, query: str, *args) -> Optional[Dict]:
        """Выполнение запроса с возвратом одной строки"""
        if not self.pool:
            raise RuntimeError("База данных не подключена")
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow(query, *args)
            return dict(row) if row else None
    
    async def fetchval(self, query: str, *args) -> Any:
        """Выполнение запроса с возвратом одного значения"""
        if not self.pool:
            raise RuntimeError("База данных не подключена")
        async with self.pool.acquire() as connection:
            return await connection.fetchval(query, *args)

# Глобальный экземпляр базы данных
db = Database()

# Функции для работы с пользователями
async def get_user_by_telegram_id(telegram_id: int) -> Optional[Dict]:
    """Получить пользователя по Telegram ID"""
    return await db.fetchrow(
        "SELECT * FROM users WHERE telegram_id = $1", 
        telegram_id
    )

async def create_user(telegram_id: int, name: str, role: str = 'student') -> Dict:
    """Создать нового пользователя"""
    return await db.fetchrow(
        """INSERT INTO users (telegram_id, name, role) 
           VALUES ($1, $2, $3) 
           RETURNING *""",
        telegram_id, name, role
    )

async def get_user_role(telegram_id: int) -> str:
    """Получить роль пользователя"""
    role = await db.fetchval(
        "SELECT role FROM users WHERE telegram_id = $1", 
        telegram_id
    )
    return role or 'student'

# Функции для работы с курсами
async def get_all_courses() -> List[Dict]:
    """Получить все курсы"""
    return await db.fetch("SELECT * FROM courses ORDER BY name")

async def add_course(name: str, description: str = None) -> Dict:
    """Добавить новый курс"""
    return await db.fetchrow(
        """INSERT INTO courses (name, description) 
           VALUES ($1, $2) 
           RETURNING *""",
        name, description
    )

async def remove_course(course_id: int) -> bool:
    """Удалить курс"""
    result = await db.execute("DELETE FROM courses WHERE id = $1", course_id)
    return result == "DELETE 1"

# Функции для работы с предметами
async def get_subjects_by_course(course_id: int) -> List[Dict]:
    """Получить предметы по курсу"""
    return await db.fetch(
        "SELECT * FROM subjects WHERE course_id = $1 ORDER BY name", 
        course_id
    )

async def get_all_subjects() -> List[Dict]:
    """Получить все предметы"""
    return await db.fetch("SELECT * FROM subjects ORDER BY name")

async def add_subject(name: str, course_id: int = None) -> Dict:
    """Добавить новый предмет"""
    return await db.fetchrow(
        """INSERT INTO subjects (name, course_id) 
           VALUES ($1, $2) 
           RETURNING *""",
        name, course_id
    )

async def remove_subject(subject_id: int) -> bool:
    """Удалить предмет"""
    result = await db.execute("DELETE FROM subjects WHERE id = $1", subject_id)
    return result == "DELETE 1"

# Функции для работы с группами
async def get_groups_by_subject(subject_id: int) -> List[Dict]:
    """Получить группы по предмету"""
    return await db.fetch(
        "SELECT * FROM groups WHERE subject_id = $1 ORDER BY name", 
        subject_id
    )

async def add_group(name: str, subject_id: int) -> Dict:
    """Добавить новую группу"""
    return await db.fetchrow(
        """INSERT INTO groups (name, subject_id) 
           VALUES ($1, $2) 
           RETURNING *""",
        name, subject_id
    )

async def remove_group(group_id: int) -> bool:
    """Удалить группу"""
    result = await db.execute("DELETE FROM groups WHERE id = $1", group_id)
    return result == "DELETE 1"

# Функции для работы с бонусными заданиями
async def get_all_bonus_tasks() -> List[Dict]:
    """Получить все бонусные задания"""
    return await db.fetch("SELECT * FROM bonus_tasks ORDER BY created_at DESC")

async def add_bonus_task(title: str, description: str, points: int = 0) -> Dict:
    """Добавить новое бонусное задание"""
    return await db.fetchrow(
        """INSERT INTO bonus_tasks (title, description, points) 
           VALUES ($1, $2, $3) 
           RETURNING *""",
        title, description, points
    )

async def remove_bonus_task(task_id: int) -> bool:
    """Удалить бонусное задание"""
    result = await db.execute("DELETE FROM bonus_tasks WHERE id = $1", task_id)
    return result == "DELETE 1"

# Функция инициализации базы данных
async def init_database():
    """Инициализация подключения к базе данных"""
    await db.connect()

# Функция закрытия соединения
async def close_database():
    """Закрытие соединения с базой данных"""
    await db.disconnect()
