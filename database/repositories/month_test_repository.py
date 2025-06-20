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
    async def create(name: str, course_id: int, subject_id: int, test_type: str = 'entry') -> MonthTest:
        """Создать новый тест месяца"""
        async with get_db_session() as session:
            # Проверяем, существует ли уже такой тест
            existing = await session.execute(
                select(MonthTest).where(
                    MonthTest.name == name,
                    MonthTest.course_id == course_id,
                    MonthTest.subject_id == subject_id,
                    MonthTest.test_type == test_type
                )
            )
            if existing.scalar_one_or_none():
                raise ValueError(f"Тест месяца '{name}' типа '{test_type}' уже существует для данного курса и предмета")

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
                subject_id=subject_id,
                test_type=test_type
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
    async def create_with_control_test(name: str, course_id: int, subject_id: int, microtopic_numbers: List[int] = None) -> tuple[MonthTest, MonthTest]:
        """
        Создать входной тест месяца и автоматически создать контрольный тест с теми же настройками
        Возвращает кортеж (входной_тест, контрольный_тест)
        """
        from .month_test_microtopic_repository import MonthTestMicrotopicRepository

        async with get_db_session() as session:
            # Создаем входной тест
            entry_test = await MonthTestRepository.create(name, course_id, subject_id, 'entry')

            # Создаем контрольный тест с тем же названием
            control_test = await MonthTestRepository.create(name, course_id, subject_id, 'control')

            # Устанавливаем связь контрольного теста с входным
            control_test.parent_test_id = entry_test.id
            session.add(control_test)
            await session.commit()
            await session.refresh(control_test)

            # Если переданы микротемы, добавляем их к обоим тестам
            if microtopic_numbers:
                for microtopic_number in microtopic_numbers:
                    # Добавляем к входному тесту
                    await MonthTestMicrotopicRepository.create(entry_test.id, microtopic_number)
                    # Добавляем к контрольному тесту
                    await MonthTestMicrotopicRepository.create(control_test.id, microtopic_number)

            return entry_test, control_test

    @staticmethod
    async def get_entry_tests() -> List[MonthTest]:
        """Получить только входные тесты месяца"""
        async with get_db_session() as session:
            result = await session.execute(
                select(MonthTest)
                .options(
                    selectinload(MonthTest.course),
                    selectinload(MonthTest.subject),
                    selectinload(MonthTest.microtopics)
                )
                .where(MonthTest.test_type == 'entry')
                .order_by(MonthTest.created_at.desc())
            )
            return list(result.scalars().all())

    @staticmethod
    async def get_control_tests() -> List[MonthTest]:
        """Получить только контрольные тесты месяца"""
        async with get_db_session() as session:
            result = await session.execute(
                select(MonthTest)
                .options(
                    selectinload(MonthTest.course),
                    selectinload(MonthTest.subject),
                    selectinload(MonthTest.microtopics),
                    selectinload(MonthTest.parent_test)
                )
                .where(MonthTest.test_type == 'control')
                .order_by(MonthTest.created_at.desc())
            )
            return list(result.scalars().all())

    @staticmethod
    async def get_control_test_by_entry_test(entry_test_id: int) -> Optional[MonthTest]:
        """Получить контрольный тест по ID входного теста"""
        async with get_db_session() as session:
            result = await session.execute(
                select(MonthTest)
                .options(
                    selectinload(MonthTest.course),
                    selectinload(MonthTest.subject),
                    selectinload(MonthTest.microtopics)
                )
                .where(
                    MonthTest.test_type == 'control',
                    MonthTest.parent_test_id == entry_test_id
                )
            )
            return result.scalar_one_or_none()

    @staticmethod
    async def delete_by_course(course_id: int) -> int:
        """Удалить все тесты месяца курса (используется при удалении курса)"""
        async with get_db_session() as session:
            result = await session.execute(delete(MonthTest).where(MonthTest.course_id == course_id))
            await session.commit()
            return result.rowcount
