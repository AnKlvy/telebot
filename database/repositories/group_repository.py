"""
Репозиторий для работы с группами
"""
from typing import List, Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from ..models import Group, Subject
from ..database import get_db_session


class GroupRepository:
    """Репозиторий для работы с группами"""
    
    @staticmethod
    async def get_all() -> List[Group]:
        """Получить все группы"""
        async with get_db_session() as session:
            result = await session.execute(
                select(Group)
                .options(selectinload(Group.subject))
                .order_by(Group.name)
            )
            return list(result.scalars().all())

    @staticmethod
    async def get_by_id(group_id: int) -> Optional[Group]:
        """Получить группу по ID"""
        async with get_db_session() as session:
            result = await session.execute(
                select(Group)
                .options(selectinload(Group.subject))
                .where(Group.id == group_id)
            )
            return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_subject(subject_id: int) -> List[Group]:
        """Получить группы по предмету"""
        async with get_db_session() as session:
            result = await session.execute(
                select(Group)
                .options(selectinload(Group.subject))
                .where(Group.subject_id == subject_id)
                .order_by(Group.name)
            )
            return list(result.scalars().all())

    @staticmethod
    async def create(name: str, subject_id: int) -> Group:
        """Создать новую группу"""
        async with get_db_session() as session:
            # Проверяем, существует ли уже такая группа для данного предмета
            existing = await session.execute(
                select(Group).where(
                    Group.name == name,
                    Group.subject_id == subject_id
                )
            )
            if existing.scalar_one_or_none():
                raise ValueError(f"Группа '{name}' уже существует для данного предмета")

            # Проверяем, существует ли предмет
            subject_exists = await session.execute(
                select(Subject).where(Subject.id == subject_id)
            )
            if not subject_exists.scalar_one_or_none():
                raise ValueError(f"Предмет с ID {subject_id} не найден")

            group = Group(name=name, subject_id=subject_id)
            session.add(group)
            await session.commit()
            await session.refresh(group)
            return group

    @staticmethod
    async def delete(group_id: int) -> bool:
        """Удалить группу"""
        async with get_db_session() as session:
            result = await session.execute(delete(Group).where(Group.id == group_id))
            await session.commit()
            return result.rowcount > 0

    @staticmethod
    async def delete_by_subject(subject_id: int) -> int:
        """Удалить все группы предмета (используется при удалении предмета)"""
        async with get_db_session() as session:
            result = await session.execute(delete(Group).where(Group.subject_id == subject_id))
            await session.commit()
            return result.rowcount

    @staticmethod
    async def exists(name: str, subject_id: int) -> bool:
        """Проверить, существует ли группа с таким именем для данного предмета"""
        async with get_db_session() as session:
            result = await session.execute(
                select(Group).where(
                    Group.name == name,
                    Group.subject_id == subject_id
                )
            )
            return result.scalar_one_or_none() is not None
