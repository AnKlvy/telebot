"""
Репозиторий для работы с пользователями
"""
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..models import User
from ..database import get_db_session


class UserRepository:
    """Репозиторий для работы с пользователями"""

    @staticmethod
    async def get_all() -> List[User]:
        """Получить всех пользователей"""
        async with get_db_session() as session:
            result = await session.execute(
                select(User).order_by(User.name)
            )
            return list(result.scalars().all())

    @staticmethod
    async def get_by_id(user_id: int) -> Optional[User]:
        """Получить пользователя по ID"""
        async with get_db_session() as session:
            result = await session.execute(
                select(User).where(User.id == user_id)
            )
            return result.scalar_one_or_none()

    @staticmethod
    async def get_by_telegram_id(telegram_id: int) -> Optional[User]:
        """Получить пользователя по Telegram ID"""
        async with get_db_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            return result.scalar_one_or_none()
    
    @staticmethod
    async def create(telegram_id: int, name: str, role: str = 'student') -> User:
        """Создать нового пользователя"""
        async with get_db_session() as session:
            user = User(telegram_id=telegram_id, name=name, role=role)
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user
    
    @staticmethod
    async def get_role(telegram_id: int) -> str:
        """Получить роль пользователя"""
        user = await UserRepository.get_by_telegram_id(telegram_id)
        return user.role if user else 'student'
