"""
Репозиторий для работы с менеджерами
"""
from typing import List, Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from ..models import Manager, User
from ..database import get_db_session


class ManagerRepository:
    """Репозиторий для работы с менеджерами"""
    
    @staticmethod
    async def get_all() -> List[Manager]:
        """Получить всех менеджеров"""
        async with get_db_session() as session:
            result = await session.execute(
                select(Manager)
                .options(selectinload(Manager.user))
            )
            return list(result.scalars().all())

    @staticmethod
    async def get_by_id(manager_id: int) -> Optional[Manager]:
        """Получить менеджера по ID"""
        async with get_db_session() as session:
            result = await session.execute(
                select(Manager)
                .options(selectinload(Manager.user))
                .where(Manager.id == manager_id)
            )
            return result.scalar_one_or_none()

    @staticmethod
    async def get_by_user_id(user_id: int) -> Optional[Manager]:
        """Получить менеджера по ID пользователя"""
        async with get_db_session() as session:
            result = await session.execute(
                select(Manager)
                .options(selectinload(Manager.user))
                .where(Manager.user_id == user_id)
            )
            return result.scalar_one_or_none()

    @staticmethod
    async def create(user_id: int) -> Manager:
        """Создать профиль менеджера"""
        async with get_db_session() as session:
            # Проверяем, существует ли уже профиль менеджера для этого пользователя
            existing = await session.execute(
                select(Manager).where(Manager.user_id == user_id)
            )
            if existing.scalar_one_or_none():
                raise ValueError(f"Профиль менеджера для пользователя {user_id} уже существует")

            # Проверяем, существует ли пользователь
            user_exists = await session.execute(
                select(User).where(User.id == user_id)
            )
            if not user_exists.scalar_one_or_none():
                raise ValueError(f"Пользователь с ID {user_id} не найден")

            manager = Manager(user_id=user_id)
            session.add(manager)
            await session.commit()
            await session.refresh(manager)
            return manager

    @staticmethod
    async def delete(manager_id: int) -> bool:
        """Удалить профиль менеджера"""
        async with get_db_session() as session:
            result = await session.execute(delete(Manager).where(Manager.id == manager_id))
            await session.commit()
            return result.rowcount > 0

    @staticmethod
    async def delete_by_user_id(user_id: int) -> bool:
        """Удалить профиль менеджера по ID пользователя"""
        async with get_db_session() as session:
            result = await session.execute(delete(Manager).where(Manager.user_id == user_id))
            await session.commit()
            return result.rowcount > 0
