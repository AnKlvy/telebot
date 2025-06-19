"""
Репозиторий для работы с покупками студентов
"""
from typing import List, Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from ..models import StudentPurchase, ShopItem, Student
from ..database import get_db_session


class StudentPurchaseRepository:
    """Репозиторий для работы с покупками студентов"""
    
    @staticmethod
    async def create_purchase(student_id: int, item_id: int, price_paid: int) -> StudentPurchase:
        """Создать новую покупку"""
        async with get_db_session() as session:
            purchase = StudentPurchase(
                student_id=student_id,
                item_id=item_id,
                price_paid=price_paid
            )
            session.add(purchase)
            await session.commit()
            await session.refresh(purchase)
            return purchase
    
    @staticmethod
    async def get_student_purchases(student_id: int) -> List[StudentPurchase]:
        """Получить все покупки студента"""
        async with get_db_session() as session:
            result = await session.execute(
                select(StudentPurchase)
                .options(selectinload(StudentPurchase.item))
                .where(StudentPurchase.student_id == student_id)
                .order_by(StudentPurchase.purchased_at.desc())
            )
            return list(result.scalars().all())
    
    @staticmethod
    async def get_unused_purchases(student_id: int, item_type: str = None) -> List[StudentPurchase]:
        """Получить неиспользованные покупки студента"""
        async with get_db_session() as session:
            query = (
                select(StudentPurchase)
                .options(selectinload(StudentPurchase.item))
                .where(StudentPurchase.student_id == student_id)
                .where(StudentPurchase.is_used == False)
            )
            
            if item_type:
                query = query.join(ShopItem).where(ShopItem.item_type == item_type)
            
            result = await session.execute(query.order_by(StudentPurchase.purchased_at.desc()))
            return list(result.scalars().all())
    
    @staticmethod
    async def mark_as_used(purchase_id: int) -> bool:
        """Отметить покупку как использованную"""
        async with get_db_session() as session:
            result = await session.execute(
                update(StudentPurchase)
                .where(StudentPurchase.id == purchase_id)
                .values(is_used=True)
            )
            await session.commit()
            return result.rowcount > 0
    
    @staticmethod
    async def get_purchase_by_id(purchase_id: int) -> Optional[StudentPurchase]:
        """Получить покупку по ID"""
        async with get_db_session() as session:
            result = await session.execute(
                select(StudentPurchase)
                .options(selectinload(StudentPurchase.item))
                .where(StudentPurchase.id == purchase_id)
            )
            return result.scalar_one_or_none()
    
    @staticmethod
    async def count_purchases_by_type(student_id: int, item_type: str) -> int:
        """Подсчитать количество покупок определенного типа"""
        async with get_db_session() as session:
            result = await session.execute(
                select(StudentPurchase)
                .join(ShopItem)
                .where(StudentPurchase.student_id == student_id)
                .where(ShopItem.item_type == item_type)
            )
            return len(list(result.scalars().all()))
