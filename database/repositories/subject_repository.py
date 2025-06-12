"""
Репозиторий для работы с предметами
"""
from typing import List, Optional
from sqlalchemy import select, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from ..models import Subject, course_subjects
from ..database import get_db_session


class SubjectRepository:
    """Репозиторий для работы с предметами"""
    
    @staticmethod
    async def get_all() -> List[Subject]:
        """Получить все предметы"""
        async with get_db_session() as session:
            result = await session.execute(
                select(Subject)
                .options(selectinload(Subject.courses))
                .order_by(Subject.name)
            )
            return list(result.scalars().all())

    @staticmethod
    async def get_by_id(subject_id: int) -> Optional[Subject]:
        """Получить предмет по ID"""
        async with get_db_session() as session:
            result = await session.execute(
                select(Subject)
                .options(selectinload(Subject.courses))
                .where(Subject.id == subject_id)
            )
            return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_course(course_id: int) -> List[Subject]:
        """Получить предметы по курсу"""
        from ..models import Course
        async with get_db_session() as session:
            result = await session.execute(
                select(Course)
                .options(selectinload(Course.subjects))
                .where(Course.id == course_id)
            )
            course = result.scalar_one_or_none()
            return list(course.subjects) if course else []

    @staticmethod
    async def create(name: str) -> Subject:
        """Создать новый предмет"""
        async with get_db_session() as session:
            # Проверяем, существует ли уже такой предмет
            existing = await session.execute(select(Subject).where(Subject.name == name))
            if existing.scalar_one_or_none():
                raise ValueError(f"Предмет '{name}' уже существует")

            subject = Subject(name=name)
            session.add(subject)
            await session.commit()
            await session.refresh(subject)
            return subject

    @staticmethod
    async def add_to_course(subject_id: int, course_id: int) -> bool:
        """Добавить предмет к курсу"""
        from ..models import Course, course_subjects
        from sqlalchemy import insert, select

        async with get_db_session() as session:
            # Проверяем, существует ли уже такая связь
            existing = await session.execute(
                select(course_subjects).where(
                    course_subjects.c.course_id == course_id,
                    course_subjects.c.subject_id == subject_id
                )
            )

            if existing.first():
                return False  # Связь уже существует

            # Добавляем связь
            await session.execute(
                insert(course_subjects).values(
                    course_id=course_id,
                    subject_id=subject_id
                )
            )
            await session.commit()
            return True
    
    @staticmethod
    async def delete(subject_id: int) -> bool:
        """Удалить предмет, все его связи с курсами и группы"""
        from ..models import course_subjects, Group
        async with get_db_session() as session:
            # Сначала удаляем все группы предмета
            await session.execute(
                delete(Group).where(Group.subject_id == subject_id)
            )

            # Затем удаляем связи с курсами
            await session.execute(
                delete(course_subjects).where(course_subjects.c.subject_id == subject_id)
            )

            # Наконец удаляем сам предмет
            result = await session.execute(delete(Subject).where(Subject.id == subject_id))
            await session.commit()
            return result.rowcount > 0
