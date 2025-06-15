"""
Репозиторий для работы с бонусными тестами
"""
from typing import List, Optional
from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from ..models import BonusTest, BonusQuestion, BonusAnswerOption
from ..database import get_db_session


class BonusTestRepository:
    """Репозиторий для работы с бонусными тестами"""
    
    @staticmethod
    async def get_all() -> List[BonusTest]:
        """Получить все бонусные тесты"""
        async with get_db_session() as session:
            result = await session.execute(
                select(BonusTest)
                .options(selectinload(BonusTest.questions))
                .order_by(BonusTest.created_at.desc())
            )
            return list(result.scalars().all())

    @staticmethod
    async def get_by_id(bonus_test_id: int) -> Optional[BonusTest]:
        """Получить бонусный тест по ID"""
        async with get_db_session() as session:
            result = await session.execute(
                select(BonusTest)
                .options(selectinload(BonusTest.questions).selectinload(BonusQuestion.answer_options))
                .where(BonusTest.id == bonus_test_id)
            )
            return result.scalar_one_or_none()

    @staticmethod
    async def create(name: str, price: int) -> BonusTest:
        """Создать новый бонусный тест"""
        async with get_db_session() as session:
            # Проверяем уникальность названия
            existing_test = await session.execute(
                select(BonusTest).where(BonusTest.name == name)
            )
            if existing_test.scalar_one_or_none():
                raise ValueError(f"Бонусный тест с названием '{name}' уже существует")

            bonus_test = BonusTest(name=name, price=price)
            session.add(bonus_test)
            await session.commit()
            await session.refresh(bonus_test)
            return bonus_test

    @staticmethod
    async def update(bonus_test_id: int, name: str = None, price: int = None) -> bool:
        """Обновить бонусный тест"""
        async with get_db_session() as session:
            bonus_test = await session.get(BonusTest, bonus_test_id)
            if not bonus_test:
                return False

            if name is not None:
                # Проверяем уникальность нового названия
                existing_test = await session.execute(
                    select(BonusTest).where(
                        BonusTest.name == name,
                        BonusTest.id != bonus_test_id
                    )
                )
                if existing_test.scalar_one_or_none():
                    raise ValueError(f"Бонусный тест с названием '{name}' уже существует")
                bonus_test.name = name

            if price is not None:
                bonus_test.price = price

            await session.commit()
            return True

    @staticmethod
    async def delete(bonus_test_id: int) -> bool:
        """Удалить бонусный тест"""
        async with get_db_session() as session:
            result = await session.execute(delete(BonusTest).where(BonusTest.id == bonus_test_id))
            await session.commit()
            return result.rowcount > 0

    @staticmethod
    async def get_count() -> int:
        """Получить количество бонусных тестов"""
        async with get_db_session() as session:
            result = await session.execute(select(func.count(BonusTest.id)))
            return result.scalar() or 0

    @staticmethod
    async def exists_by_name(name: str) -> bool:
        """Проверить, существует ли бонусный тест с таким названием"""
        async with get_db_session() as session:
            result = await session.execute(
                select(BonusTest).where(BonusTest.name == name)
            )
            return result.scalar_one_or_none() is not None
