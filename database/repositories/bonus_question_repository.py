"""
Репозиторий для работы с вопросами бонусных тестов
"""
from typing import List, Optional, Type
from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from ..models import BonusTest, BonusQuestion, BonusAnswerOption
from ..database import get_db_session
from .base_question_repository import BaseQuestionRepository


class BonusQuestionRepository(BaseQuestionRepository):
    """Репозиторий для работы с вопросами бонусных тестов"""
    
    # Реализация абстрактных свойств базового класса
    @property
    def question_model(self) -> Type:
        return BonusQuestion
    
    @property
    def answer_option_model(self) -> Type:
        return BonusAnswerOption
    
    @property
    def parent_id_field(self) -> str:
        return 'bonus_test_id'
    
    @property
    def parent_model(self) -> Type:
        return BonusTest
    
    # Специфичные методы для бонусных тестов
    async def create(self, bonus_test_id: int, text: str, photo_path: Optional[str] = None, 
                    time_limit: int = 30) -> BonusQuestion:
        """Создать новый вопрос для бонусного теста"""
        # Используем базовый метод создания (без дополнительных параметров)
        return await self.create_question(
            parent_id=bonus_test_id,
            text=text,
            photo_path=photo_path,
            time_limit=time_limit
        )

    async def get_by_bonus_test(self, bonus_test_id: int) -> List[BonusQuestion]:
        """Получить все вопросы бонусного теста"""
        return await self.get_by_parent(bonus_test_id)

    async def get_next_order_number(self, bonus_test_id: int) -> int:
        """Получить следующий порядковый номер для вопроса в бонусном тесте"""
        return await super().get_next_order_number(bonus_test_id)

    async def get_count_by_bonus_test(self, bonus_test_id: int) -> int:
        """Получить количество вопросов в бонусном тесте"""
        return await self.get_count_by_parent(bonus_test_id)

    async def delete_by_bonus_test(self, bonus_test_id: int) -> int:
        """Удалить все вопросы бонусного теста"""
        return await self.delete_by_parent(bonus_test_id)
