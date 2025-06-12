"""
Репозиторий для работы с уроками
"""
from typing import List, Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from ..models import Lesson, Subject
from ..database import get_db_session


class LessonRepository:
    """Репозиторий для работы с уроками"""
    
    @staticmethod
    async def get_all() -> List[Lesson]:
        """Получить все уроки"""
        async with get_db_session() as session:
            result = await session.execute(
                select(Lesson)
                .options(selectinload(Lesson.subject))
                .order_by(Lesson.subject_id, Lesson.name)
            )
            return list(result.scalars().all())

    @staticmethod
    async def get_by_id(lesson_id: int) -> Optional[Lesson]:
        """Получить урок по ID"""
        async with get_db_session() as session:
            result = await session.execute(
                select(Lesson)
                .options(selectinload(Lesson.subject))
                .where(Lesson.id == lesson_id)
            )
            return result.scalar_one_or_none()

    @staticmethod
    async def get_by_subject(subject_id: int) -> List[Lesson]:
        """Получить уроки по предмету"""
        async with get_db_session() as session:
            result = await session.execute(
                select(Lesson)
                .options(selectinload(Lesson.subject))
                .where(Lesson.subject_id == subject_id)
                .order_by(Lesson.name)
            )
            return list(result.scalars().all())

    @staticmethod
    async def create(name: str, subject_id: int) -> Lesson:
        """Создать новый урок"""
        async with get_db_session() as session:
            # Проверяем, существует ли уже такой урок для данного предмета
            existing = await session.execute(
                select(Lesson).where(
                    Lesson.name == name,
                    Lesson.subject_id == subject_id
                )
            )
            if existing.scalar_one_or_none():
                raise ValueError(f"Урок '{name}' уже существует для данного предмета")

            # Проверяем, существует ли предмет
            subject_exists = await session.execute(
                select(Subject).where(Subject.id == subject_id)
            )
            if not subject_exists.scalar_one_or_none():
                raise ValueError(f"Предмет с ID {subject_id} не найден")

            lesson = Lesson(name=name, subject_id=subject_id)
            session.add(lesson)
            await session.commit()
            await session.refresh(lesson)
            return lesson

    @staticmethod
    async def update(lesson_id: int, name: str = None) -> Optional[Lesson]:
        """Обновить урок"""
        async with get_db_session() as session:
            result = await session.execute(
                select(Lesson).where(Lesson.id == lesson_id)
            )
            lesson = result.scalar_one_or_none()
            
            if not lesson:
                return None

            if name is not None:
                # Проверяем уникальность нового названия в рамках предмета
                existing = await session.execute(
                    select(Lesson).where(
                        Lesson.name == name,
                        Lesson.subject_id == lesson.subject_id,
                        Lesson.id != lesson_id
                    )
                )
                if existing.scalar_one_or_none():
                    raise ValueError(f"Урок '{name}' уже существует для данного предмета")
                
                lesson.name = name

            await session.commit()
            await session.refresh(lesson)
            return lesson

    @staticmethod
    async def delete(lesson_id: int) -> bool:
        """Удалить урок"""
        async with get_db_session() as session:
            result = await session.execute(
                delete(Lesson).where(Lesson.id == lesson_id)
            )
            await session.commit()
            return result.rowcount > 0

    @staticmethod
    async def get_by_name_and_subject(name: str, subject_id: int) -> Optional[Lesson]:
        """Получить урок по названию и предмету"""
        async with get_db_session() as session:
            result = await session.execute(
                select(Lesson)
                .options(selectinload(Lesson.subject))
                .where(
                    Lesson.name == name,
                    Lesson.subject_id == subject_id
                )
            )
            return result.scalar_one_or_none()
