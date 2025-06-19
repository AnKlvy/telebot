"""
Репозиторий для работы с покупками бонусных тестов студентами
"""
from typing import List, Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from ..models import StudentBonusTest, BonusTest, Student
from ..database import get_db_session


class StudentBonusTestRepository:
    """Репозиторий для работы с покупками бонусных тестов студентами"""
    
    @staticmethod
    async def create_purchase(student_id: int, bonus_test_id: int, price_paid: int) -> StudentBonusTest:
        """Создать новую покупку бонусного теста"""
        async with get_db_session() as session:
            purchase = StudentBonusTest(
                student_id=student_id,
                bonus_test_id=bonus_test_id,
                price_paid=price_paid
            )
            session.add(purchase)
            await session.commit()
            await session.refresh(purchase)
            return purchase
    
    @staticmethod
    async def get_student_bonus_tests(student_id: int) -> List[StudentBonusTest]:
        """Получить все купленные бонусные тесты студента"""
        async with get_db_session() as session:
            result = await session.execute(
                select(StudentBonusTest)
                .options(
                    selectinload(StudentBonusTest.bonus_test)
                    .selectinload(BonusTest.questions)
                )
                .where(StudentBonusTest.student_id == student_id)
                .order_by(StudentBonusTest.purchased_at.desc())
            )
            return list(result.scalars().all())
    
    @staticmethod
    async def get_unused_bonus_tests(student_id: int) -> List[StudentBonusTest]:
        """Получить неиспользованные (непройденные) бонусные тесты студента"""
        async with get_db_session() as session:
            result = await session.execute(
                select(StudentBonusTest)
                .options(
                    selectinload(StudentBonusTest.bonus_test)
                    .selectinload(BonusTest.questions)
                )
                .where(StudentBonusTest.student_id == student_id)
                .where(StudentBonusTest.is_used == False)
                .order_by(StudentBonusTest.purchased_at.desc())
            )
            return list(result.scalars().all())
    
    @staticmethod
    async def mark_as_used(purchase_id: int) -> bool:
        """Отметить бонусный тест как пройденный"""
        async with get_db_session() as session:
            result = await session.execute(
                update(StudentBonusTest)
                .where(StudentBonusTest.id == purchase_id)
                .values(is_used=True)
            )
            await session.commit()
            return result.rowcount > 0
    
    @staticmethod
    async def get_purchase_by_id(purchase_id: int) -> Optional[StudentBonusTest]:
        """Получить покупку бонусного теста по ID"""
        async with get_db_session() as session:
            result = await session.execute(
                select(StudentBonusTest)
                .options(selectinload(StudentBonusTest.bonus_test))
                .where(StudentBonusTest.id == purchase_id)
            )
            return result.scalar_one_or_none()
    
    @staticmethod
    async def has_purchased_test(student_id: int, bonus_test_id: int) -> bool:
        """Проверить, покупал ли студент данный бонусный тест"""
        async with get_db_session() as session:
            result = await session.execute(
                select(StudentBonusTest)
                .where(StudentBonusTest.student_id == student_id)
                .where(StudentBonusTest.bonus_test_id == bonus_test_id)
            )
            return result.scalar_one_or_none() is not None
    
    @staticmethod
    async def count_purchases_by_test(bonus_test_id: int) -> int:
        """Подсчитать количество покупок определенного бонусного теста"""
        async with get_db_session() as session:
            result = await session.execute(
                select(StudentBonusTest)
                .where(StudentBonusTest.bonus_test_id == bonus_test_id)
            )
            return len(list(result.scalars().all()))
