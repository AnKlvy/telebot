"""
Репозиторий для работы со связями тестов месяца и микротем
"""
from typing import List, Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from ..models import MonthTestMicrotopic, MonthTest
from ..database import get_db_session


class MonthTestMicrotopicRepository:
    """Репозиторий для работы со связями тестов месяца и микротем"""
    
    @staticmethod
    async def get_all() -> List[MonthTestMicrotopic]:
        """Получить все связи тестов месяца с микротемами"""
        async with get_db_session() as session:
            result = await session.execute(
                select(MonthTestMicrotopic)
                .options(selectinload(MonthTestMicrotopic.month_test))
                .order_by(MonthTestMicrotopic.month_test_id, MonthTestMicrotopic.microtopic_number)
            )
            return list(result.scalars().all())

    @staticmethod
    async def get_by_month_test(month_test_id: int) -> List[MonthTestMicrotopic]:
        """Получить все микротемы для теста месяца"""
        async with get_db_session() as session:
            result = await session.execute(
                select(MonthTestMicrotopic)
                .options(selectinload(MonthTestMicrotopic.month_test))
                .where(MonthTestMicrotopic.month_test_id == month_test_id)
                .order_by(MonthTestMicrotopic.microtopic_number)
            )
            return list(result.scalars().all())

    @staticmethod
    async def get_microtopic_numbers_by_month_test(month_test_id: int) -> List[int]:
        """Получить список номеров микротем для теста месяца"""
        async with get_db_session() as session:
            result = await session.execute(
                select(MonthTestMicrotopic.microtopic_number)
                .where(MonthTestMicrotopic.month_test_id == month_test_id)
                .order_by(MonthTestMicrotopic.microtopic_number)
            )
            return list(result.scalars().all())

    @staticmethod
    async def create(month_test_id: int, microtopic_number: int) -> MonthTestMicrotopic:
        """Создать новую связь теста месяца с микротемой"""
        async with get_db_session() as session:
            # Проверяем, существует ли уже такая связь
            existing = await session.execute(
                select(MonthTestMicrotopic).where(
                    MonthTestMicrotopic.month_test_id == month_test_id,
                    MonthTestMicrotopic.microtopic_number == microtopic_number
                )
            )
            if existing.scalar_one_or_none():
                raise ValueError(f"Микротема {microtopic_number} уже привязана к тесту месяца {month_test_id}")

            # Проверяем, существует ли тест месяца
            month_test_exists = await session.execute(
                select(MonthTest).where(MonthTest.id == month_test_id)
            )
            if not month_test_exists.scalar_one_or_none():
                raise ValueError(f"Тест месяца с ID {month_test_id} не найден")

            month_test_microtopic = MonthTestMicrotopic(
                month_test_id=month_test_id,
                microtopic_number=microtopic_number
            )
            session.add(month_test_microtopic)
            await session.commit()
            await session.refresh(month_test_microtopic)
            return month_test_microtopic

    @staticmethod
    async def create_multiple(month_test_id: int, microtopic_numbers: List[int]) -> List[MonthTestMicrotopic]:
        """Создать несколько связей теста месяца с микротемами"""
        async with get_db_session() as session:
            # Проверяем, существует ли тест месяца
            month_test_exists = await session.execute(
                select(MonthTest).where(MonthTest.id == month_test_id)
            )
            if not month_test_exists.scalar_one_or_none():
                raise ValueError(f"Тест месяца с ID {month_test_id} не найден")

            # Получаем уже существующие связи
            existing_result = await session.execute(
                select(MonthTestMicrotopic.microtopic_number)
                .where(MonthTestMicrotopic.month_test_id == month_test_id)
            )
            existing_numbers = set(existing_result.scalars().all())

            # Создаем только новые связи
            created_relations = []
            for microtopic_number in microtopic_numbers:
                if microtopic_number not in existing_numbers:
                    month_test_microtopic = MonthTestMicrotopic(
                        month_test_id=month_test_id,
                        microtopic_number=microtopic_number
                    )
                    session.add(month_test_microtopic)
                    created_relations.append(month_test_microtopic)

            if created_relations:
                await session.commit()
                for relation in created_relations:
                    await session.refresh(relation)

            return created_relations

    @staticmethod
    async def delete_by_month_test_and_microtopic(month_test_id: int, microtopic_number: int) -> bool:
        """Удалить связь теста месяца с конкретной микротемой"""
        async with get_db_session() as session:
            result = await session.execute(
                delete(MonthTestMicrotopic).where(
                    MonthTestMicrotopic.month_test_id == month_test_id,
                    MonthTestMicrotopic.microtopic_number == microtopic_number
                )
            )
            await session.commit()
            return result.rowcount > 0

    @staticmethod
    async def delete_by_month_test(month_test_id: int) -> int:
        """Удалить все связи теста месяца с микротемами"""
        async with get_db_session() as session:
            result = await session.execute(
                delete(MonthTestMicrotopic).where(MonthTestMicrotopic.month_test_id == month_test_id)
            )
            await session.commit()
            return result.rowcount

    @staticmethod
    async def replace_microtopics(month_test_id: int, microtopic_numbers: List[int]) -> List[MonthTestMicrotopic]:
        """Заменить все микротемы теста месяца на новые"""
        async with get_db_session() as session:
            # Удаляем все существующие связи
            await session.execute(
                delete(MonthTestMicrotopic).where(MonthTestMicrotopic.month_test_id == month_test_id)
            )

            # Создаем новые связи
            created_relations = []
            for microtopic_number in microtopic_numbers:
                month_test_microtopic = MonthTestMicrotopic(
                    month_test_id=month_test_id,
                    microtopic_number=microtopic_number
                )
                session.add(month_test_microtopic)
                created_relations.append(month_test_microtopic)

            await session.commit()
            for relation in created_relations:
                await session.refresh(relation)

            return created_relations
