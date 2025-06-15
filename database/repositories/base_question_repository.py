"""
Базовый репозиторий для работы с вопросами (обычными и бонусными)
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Type, Any
from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from ..database import get_db_session


class BaseQuestionRepository(ABC):
    """Базовый класс для репозиториев вопросов"""
    
    @property
    @abstractmethod
    def question_model(self) -> Type:
        """Модель вопроса"""
        pass
    
    @property
    @abstractmethod
    def answer_option_model(self) -> Type:
        """Модель варианта ответа"""
        pass
    
    @property
    @abstractmethod
    def parent_id_field(self) -> str:
        """Название поля родительского ID (homework_id или bonus_test_id)"""
        pass
    
    @property
    @abstractmethod
    def parent_model(self) -> Type:
        """Модель родителя (Homework или BonusTest)"""
        pass
    
    async def get_all(self) -> List[Any]:
        """Получить все вопросы"""
        async with get_db_session() as session:
            result = await session.execute(
                select(self.question_model)
                .options(selectinload(getattr(self.question_model, 'answer_options')))
                .order_by(
                    getattr(self.question_model, self.parent_id_field),
                    getattr(self.question_model, 'order_number')
                )
            )
            return list(result.scalars().all())

    async def get_by_id(self, question_id: int) -> Optional[Any]:
        """Получить вопрос по ID"""
        async with get_db_session() as session:
            result = await session.execute(
                select(self.question_model)
                .options(selectinload(getattr(self.question_model, 'answer_options')))
                .where(getattr(self.question_model, 'id') == question_id)
            )
            return result.scalar_one_or_none()

    async def get_by_parent(self, parent_id: int) -> List[Any]:
        """Получить вопросы по родительскому ID"""
        async with get_db_session() as session:
            result = await session.execute(
                select(self.question_model)
                .options(selectinload(getattr(self.question_model, 'answer_options')))
                .where(getattr(self.question_model, self.parent_id_field) == parent_id)
                .order_by(getattr(self.question_model, 'order_number'))
            )
            return list(result.scalars().all())

    async def get_next_order_number(self, parent_id: int) -> int:
        """Получить следующий порядковый номер для вопроса"""
        async with get_db_session() as session:
            result = await session.execute(
                select(func.max(getattr(self.question_model, 'order_number')))
                .where(getattr(self.question_model, self.parent_id_field) == parent_id)
            )
            max_order = result.scalar()
            return (max_order or 0) + 1

    async def _validate_parent_exists(self, session: AsyncSession, parent_id: int) -> bool:
        """Проверить существование родительской сущности"""
        result = await session.execute(
            select(self.parent_model).where(getattr(self.parent_model, 'id') == parent_id)
        )
        return result.scalar_one_or_none() is not None

    async def create_question(self, parent_id: int, text: str, photo_path: Optional[str] = None, 
                             time_limit: int = 30, **kwargs) -> Any:
        """Создать новый вопрос"""
        async with get_db_session() as session:
            # Проверяем существование родительской сущности
            if not await self._validate_parent_exists(session, parent_id):
                parent_name = self.parent_model.__name__
                raise ValueError(f"{parent_name} с ID {parent_id} не найден")

            # Получаем следующий порядковый номер
            order_number = await self.get_next_order_number(parent_id)

            # Создаем базовые параметры
            question_params = {
                self.parent_id_field: parent_id,
                'text': text,
                'photo_path': photo_path,
                'time_limit': time_limit,
                'order_number': order_number
            }
            
            # Добавляем дополнительные параметры
            question_params.update(kwargs)

            question = self.question_model(**question_params)
            session.add(question)
            await session.commit()
            await session.refresh(question)
            return question

    async def update(self, question_id: int, text: str = None, photo_path: str = None, 
                    time_limit: int = None, **kwargs) -> bool:
        """Обновить вопрос"""
        async with get_db_session() as session:
            question = await session.get(self.question_model, question_id)
            if not question:
                return False

            if text is not None:
                question.text = text
            if photo_path is not None:
                question.photo_path = photo_path
            if time_limit is not None:
                question.time_limit = time_limit
            
            # Обновляем дополнительные поля
            for key, value in kwargs.items():
                if hasattr(question, key) and value is not None:
                    setattr(question, key, value)

            await session.commit()
            return True

    async def delete(self, question_id: int) -> bool:
        """Удалить вопрос"""
        async with get_db_session() as session:
            result = await session.execute(
                delete(self.question_model).where(getattr(self.question_model, 'id') == question_id)
            )
            await session.commit()
            return result.rowcount > 0

    async def delete_by_parent(self, parent_id: int) -> int:
        """Удалить все вопросы родительской сущности"""
        async with get_db_session() as session:
            result = await session.execute(
                delete(self.question_model).where(getattr(self.question_model, self.parent_id_field) == parent_id)
            )
            await session.commit()
            return result.rowcount

    async def get_count_by_parent(self, parent_id: int) -> int:
        """Получить количество вопросов у родительской сущности"""
        async with get_db_session() as session:
            result = await session.execute(
                select(func.count(getattr(self.question_model, 'id')))
                .where(getattr(self.question_model, self.parent_id_field) == parent_id)
            )
            return result.scalar() or 0
