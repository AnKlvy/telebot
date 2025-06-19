"""
Репозиторий для работы с товарами магазина
"""
from typing import List, Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from ..models import ShopItem
from ..database import get_db_session


class ShopItemRepository:
    """Репозиторий для работы с товарами магазина"""
    
    @staticmethod
    async def get_all_active() -> List[ShopItem]:
        """Получить все активные товары"""
        async with get_db_session() as session:
            result = await session.execute(
                select(ShopItem)
                .where(ShopItem.is_active == True)
                .order_by(ShopItem.price)
            )
            return list(result.scalars().all())
    
    @staticmethod
    async def get_by_id(item_id: int) -> Optional[ShopItem]:
        """Получить товар по ID"""
        async with get_db_session() as session:
            result = await session.execute(
                select(ShopItem)
                .where(ShopItem.id == item_id)
            )
            return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_type(item_type: str) -> List[ShopItem]:
        """Получить товары по типу"""
        async with get_db_session() as session:
            result = await session.execute(
                select(ShopItem)
                .where(ShopItem.item_type == item_type)
                .where(ShopItem.is_active == True)
                .order_by(ShopItem.price)
            )
            return list(result.scalars().all())
    
    @staticmethod
    async def create(name: str, description: str, price: int, item_type: str) -> ShopItem:
        """Создать новый товар"""
        async with get_db_session() as session:
            item = ShopItem(
                name=name,
                description=description,
                price=price,
                item_type=item_type
            )
            session.add(item)
            await session.commit()
            await session.refresh(item)
            return item
    
    @staticmethod
    async def update_price(item_id: int, new_price: int) -> bool:
        """Обновить цену товара"""
        async with get_db_session() as session:
            result = await session.execute(
                update(ShopItem)
                .where(ShopItem.id == item_id)
                .values(price=new_price)
            )
            await session.commit()
            return result.rowcount > 0
    
    @staticmethod
    async def deactivate(item_id: int) -> bool:
        """Деактивировать товар"""
        async with get_db_session() as session:
            result = await session.execute(
                update(ShopItem)
                .where(ShopItem.id == item_id)
                .values(is_active=False)
            )
            await session.commit()
            return result.rowcount > 0
