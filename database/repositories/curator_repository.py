"""
Репозиторий для работы с кураторами
"""
from typing import List, Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from ..models import Curator, User, Course, Subject, Group
from ..database import get_db_session


class CuratorRepository:
    """Репозиторий для работы с кураторами"""
    
    @staticmethod
    async def get_all() -> List[Curator]:
        """Получить всех кураторов"""
        async with get_db_session() as session:
            result = await session.execute(
                select(Curator)
                .options(
                    selectinload(Curator.user),
                    selectinload(Curator.course),
                    selectinload(Curator.subject),
                    selectinload(Curator.group).selectinload(Group.subject)
                )
            )
            return list(result.scalars().all())

    @staticmethod
    async def get_by_id(curator_id: int) -> Optional[Curator]:
        """Получить куратора по ID"""
        async with get_db_session() as session:
            result = await session.execute(
                select(Curator)
                .options(
                    selectinload(Curator.user),
                    selectinload(Curator.course),
                    selectinload(Curator.subject),
                    selectinload(Curator.group).selectinload(Group.subject)
                )
                .where(Curator.id == curator_id)
            )
            return result.scalar_one_or_none()

    @staticmethod
    async def get_by_user_id(user_id: int) -> Optional[Curator]:
        """Получить куратора по ID пользователя"""
        async with get_db_session() as session:
            result = await session.execute(
                select(Curator)
                .options(
                    selectinload(Curator.user),
                    selectinload(Curator.course),
                    selectinload(Curator.subject),
                    selectinload(Curator.group).selectinload(Group.subject)
                )
                .where(Curator.user_id == user_id)
            )
            return result.scalar_one_or_none()

    @staticmethod
    async def get_by_group(group_id: int) -> List[Curator]:
        """Получить кураторов по группе"""
        async with get_db_session() as session:
            result = await session.execute(
                select(Curator)
                .options(
                    selectinload(Curator.user),
                    selectinload(Curator.course),
                    selectinload(Curator.subject),
                    selectinload(Curator.group).selectinload(Group.subject)
                )
                .where(Curator.group_id == group_id)
            )
            return list(result.scalars().all())

    @staticmethod
    async def get_by_subject_and_group(subject_id: int = None, group_id: int = None) -> List[Curator]:
        """Получить кураторов по предмету и/или группе"""
        async with get_db_session() as session:
            query = select(Curator).options(
                selectinload(Curator.user),
                selectinload(Curator.course),
                selectinload(Curator.subject),
                selectinload(Curator.group).selectinload(Group.subject)
            )
            
            if group_id:
                query = query.where(Curator.group_id == group_id)
            elif subject_id:
                query = query.where(Curator.subject_id == subject_id)
                
            result = await session.execute(query)
            return list(result.scalars().all())

    @staticmethod
    async def create(user_id: int, course_id: int = None, subject_id: int = None, group_id: int = None) -> Curator:
        """Создать профиль куратора"""
        async with get_db_session() as session:
            # Проверяем, существует ли уже профиль куратора для этого пользователя
            existing = await session.execute(
                select(Curator).where(Curator.user_id == user_id)
            )
            if existing.scalar_one_or_none():
                raise ValueError(f"Профиль куратора для пользователя {user_id} уже существует")

            # Проверяем, существует ли пользователь
            user_exists = await session.execute(
                select(User).where(User.id == user_id)
            )
            if not user_exists.scalar_one_or_none():
                raise ValueError(f"Пользователь с ID {user_id} не найден")

            curator = Curator(
                user_id=user_id,
                course_id=course_id,
                subject_id=subject_id,
                group_id=group_id
            )
            session.add(curator)
            await session.commit()
            await session.refresh(curator)
            return curator

    @staticmethod
    async def update(curator_id: int, course_id: int = None, subject_id: int = None, group_id: int = None) -> bool:
        """Обновить информацию о кураторе"""
        async with get_db_session() as session:
            curator = await session.get(Curator, curator_id)
            if not curator:
                return False
            
            if course_id is not None:
                curator.course_id = course_id
            if subject_id is not None:
                curator.subject_id = subject_id
            if group_id is not None:
                curator.group_id = group_id
                
            await session.commit()
            return True

    @staticmethod
    async def delete(curator_id: int) -> bool:
        """Удалить профиль куратора"""
        async with get_db_session() as session:
            result = await session.execute(delete(Curator).where(Curator.id == curator_id))
            await session.commit()
            return result.rowcount > 0

    @staticmethod
    async def delete_by_user_id(user_id: int) -> bool:
        """Удалить профиль куратора по ID пользователя"""
        async with get_db_session() as session:
            result = await session.execute(delete(Curator).where(Curator.user_id == user_id))
            await session.commit()
            return result.rowcount > 0
