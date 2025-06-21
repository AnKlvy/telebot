"""
Репозиторий для работы с тестами месяца
"""
from typing import List, Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from ..models import MonthTest, Course, Subject
from ..database import get_db_session


class MonthTestRepository:
    """Репозиторий для работы с тестами месяца"""
    
    @staticmethod
    async def get_all() -> List[MonthTest]:
        """Получить все тесты месяца"""
        async with get_db_session() as session:
            result = await session.execute(
                select(MonthTest)
                .options(
                    selectinload(MonthTest.course),
                    selectinload(MonthTest.subject),
                    selectinload(MonthTest.microtopics)
                )
                .order_by(MonthTest.created_at.desc())
            )
            return list(result.scalars().all())

    @staticmethod
    async def get_by_id(month_test_id: int) -> Optional[MonthTest]:
        """Получить тест месяца по ID"""
        async with get_db_session() as session:
            result = await session.execute(
                select(MonthTest)
                .options(
                    selectinload(MonthTest.course),
                    selectinload(MonthTest.subject),
                    selectinload(MonthTest.microtopics)
                )
                .where(MonthTest.id == month_test_id)
            )
            return result.scalar_one_or_none()

    @staticmethod
    async def get_by_course_subject(course_id: int, subject_id: int) -> List[MonthTest]:
        """Получить тесты месяца по курсу и предмету"""
        async with get_db_session() as session:
            result = await session.execute(
                select(MonthTest)
                .options(
                    selectinload(MonthTest.course),
                    selectinload(MonthTest.subject),
                    selectinload(MonthTest.microtopics)
                )
                .where(
                    MonthTest.course_id == course_id,
                    MonthTest.subject_id == subject_id
                )
                .order_by(MonthTest.name)
            )
            return list(result.scalars().all())

    @staticmethod
    async def get_by_course_subject_month(course_id: int, subject_id: int, month_name: str) -> Optional[MonthTest]:
        """Получить тест месяца по курсу, предмету и названию месяца"""
        async with get_db_session() as session:
            result = await session.execute(
                select(MonthTest)
                .options(
                    selectinload(MonthTest.course),
                    selectinload(MonthTest.subject),
                    selectinload(MonthTest.microtopics)
                )
                .where(
                    MonthTest.course_id == course_id,
                    MonthTest.subject_id == subject_id,
                    MonthTest.name == month_name
                )
            )
            return result.scalar_one_or_none()

    @staticmethod
    async def create(name: str, course_id: int, subject_id: int) -> MonthTest:
        """Создать новый тест месяца"""
        async with get_db_session() as session:
            # Проверяем, существует ли уже такой тест
            existing = await session.execute(
                select(MonthTest).where(
                    MonthTest.name == name,
                    MonthTest.course_id == course_id,
                    MonthTest.subject_id == subject_id
                )
            )
            if existing.scalar_one_or_none():
                raise ValueError(f"Тест месяца '{name}' уже существует для данного курса и предмета")

            # Проверяем, существует ли курс
            course_exists = await session.execute(
                select(Course).where(Course.id == course_id)
            )
            if not course_exists.scalar_one_or_none():
                raise ValueError(f"Курс с ID {course_id} не найден")

            # Проверяем, существует ли предмет
            subject_exists = await session.execute(
                select(Subject).where(Subject.id == subject_id)
            )
            if not subject_exists.scalar_one_or_none():
                raise ValueError(f"Предмет с ID {subject_id} не найден")



            month_test = MonthTest(
                name=name,
                course_id=course_id,
                subject_id=subject_id
            )
            session.add(month_test)
            await session.commit()
            await session.refresh(month_test)
            return month_test

    @staticmethod
    async def delete(month_test_id: int) -> bool:
        """Удалить тест месяца"""
        async with get_db_session() as session:
            result = await session.execute(delete(MonthTest).where(MonthTest.id == month_test_id))
            await session.commit()
            return result.rowcount > 0

    @staticmethod
    async def exists_by_name_course_subject(name: str, course_id: int, subject_id: int) -> bool:
        """Проверить, существует ли тест месяца с таким названием для курса и предмета"""
        async with get_db_session() as session:
            result = await session.execute(
                select(MonthTest).where(
                    MonthTest.name == name,
                    MonthTest.course_id == course_id,
                    MonthTest.subject_id == subject_id
                )
            )
            return result.scalar_one_or_none() is not None

    @staticmethod
    async def get_by_subject(subject_id: int) -> List[MonthTest]:
        """Получить все тесты месяца по предмету"""
        async with get_db_session() as session:
            result = await session.execute(
                select(MonthTest)
                .options(
                    selectinload(MonthTest.course),
                    selectinload(MonthTest.subject),
                    selectinload(MonthTest.microtopics)
                )
                .where(MonthTest.subject_id == subject_id)
                .order_by(MonthTest.name)
            )
            return list(result.scalars().all())

    @staticmethod
    async def delete_by_subject(subject_id: int) -> int:
        """Удалить все тесты месяца предмета (используется при удалении предмета)"""
        async with get_db_session() as session:
            result = await session.execute(delete(MonthTest).where(MonthTest.subject_id == subject_id))
            await session.commit()
            return result.rowcount





    @staticmethod
    async def delete_by_course(course_id: int) -> int:
        """Удалить все тесты месяца курса (используется при удалении курса)"""
        async with get_db_session() as session:
            result = await session.execute(delete(MonthTest).where(MonthTest.course_id == course_id))
            await session.commit()
            return result.rowcount
