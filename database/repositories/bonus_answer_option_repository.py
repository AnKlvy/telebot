"""
Репозиторий для работы с вариантами ответов бонусных тестов
"""
from typing import List, Optional
from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from ..models import BonusQuestion, BonusAnswerOption
from ..database import get_db_session


class BonusAnswerOptionRepository:
    """Репозиторий для работы с вариантами ответов бонусных тестов"""
    
    @staticmethod
    async def get_all() -> List[BonusAnswerOption]:
        """Получить все варианты ответов"""
        async with get_db_session() as session:
            result = await session.execute(
                select(BonusAnswerOption)
                .options(selectinload(BonusAnswerOption.bonus_question))
                .order_by(BonusAnswerOption.bonus_question_id, BonusAnswerOption.order_number)
            )
            return list(result.scalars().all())

    @staticmethod
    async def get_by_id(answer_option_id: int) -> Optional[BonusAnswerOption]:
        """Получить вариант ответа по ID"""
        async with get_db_session() as session:
            result = await session.execute(
                select(BonusAnswerOption)
                .options(selectinload(BonusAnswerOption.bonus_question))
                .where(BonusAnswerOption.id == answer_option_id)
            )
            return result.scalar_one_or_none()

    @staticmethod
    async def get_by_bonus_question(bonus_question_id: int) -> List[BonusAnswerOption]:
        """Получить варианты ответов по вопросу"""
        import logging
        async with get_db_session() as session:
            result = await session.execute(
                select(BonusAnswerOption)
                .where(BonusAnswerOption.bonus_question_id == bonus_question_id)
                .order_by(BonusAnswerOption.order_number)
            )
            options = list(result.scalars().all())

            return options

    @staticmethod
    async def get_next_order_number(bonus_question_id: int) -> int:
        """Получить следующий порядковый номер для варианта ответа"""
        async with get_db_session() as session:
            result = await session.execute(
                select(func.max(BonusAnswerOption.order_number))
                .where(BonusAnswerOption.bonus_question_id == bonus_question_id)
            )
            max_order = result.scalar()
            return (max_order or 0) + 1

    @staticmethod
    async def create(bonus_question_id: int, text: str, is_correct: bool = False) -> BonusAnswerOption:
        """Создать новый вариант ответа"""
        async with get_db_session() as session:
            # Проверяем существование вопроса
            question_exists = await session.execute(
                select(BonusQuestion).where(BonusQuestion.id == bonus_question_id)
            )
            if not question_exists.scalar_one_or_none():
                raise ValueError(f"Бонусный вопрос с ID {bonus_question_id} не найден")

            # Получаем следующий порядковый номер
            order_number = await BonusAnswerOptionRepository.get_next_order_number(bonus_question_id)

            answer_option = BonusAnswerOption(
                bonus_question_id=bonus_question_id,
                text=text,
                is_correct=is_correct,
                order_number=order_number
            )
            session.add(answer_option)
            await session.commit()
            await session.refresh(answer_option)
            return answer_option

    @staticmethod
    async def create_multiple(bonus_question_id: int, options: List[dict]) -> List[BonusAnswerOption]:
        """
        Создать несколько вариантов ответов одновременно
        options: список словарей с ключами 'text' и 'is_correct'
        """
        async with get_db_session() as session:
            # Проверяем существование вопроса
            question_exists = await session.execute(
                select(BonusQuestion).where(BonusQuestion.id == bonus_question_id)
            )
            if not question_exists.scalar_one_or_none():
                raise ValueError(f"Бонусный вопрос с ID {bonus_question_id} не найден")

            # Получаем начальный порядковый номер
            start_order = await BonusAnswerOptionRepository.get_next_order_number(bonus_question_id)

            answer_options = []
            for i, option in enumerate(options):
                answer_option = BonusAnswerOption(
                    bonus_question_id=bonus_question_id,
                    text=option['text'],
                    is_correct=option.get('is_correct', False),
                    order_number=start_order + i
                )
                session.add(answer_option)
                answer_options.append(answer_option)

            await session.commit()

            # Обновляем объекты для получения ID
            for answer_option in answer_options:
                await session.refresh(answer_option)

            return answer_options

    @staticmethod
    async def update(answer_option_id: int, text: str = None, is_correct: bool = None) -> bool:
        """Обновить вариант ответа"""
        async with get_db_session() as session:
            answer_option = await session.get(BonusAnswerOption, answer_option_id)
            if not answer_option:
                return False

            if text is not None:
                answer_option.text = text
            if is_correct is not None:
                answer_option.is_correct = is_correct

            await session.commit()
            return True

    @staticmethod
    async def delete(answer_option_id: int) -> bool:
        """Удалить вариант ответа"""
        async with get_db_session() as session:
            result = await session.execute(delete(BonusAnswerOption).where(BonusAnswerOption.id == answer_option_id))
            await session.commit()
            return result.rowcount > 0

    @staticmethod
    async def delete_by_bonus_question(bonus_question_id: int) -> int:
        """Удалить все варианты ответов вопроса"""
        async with get_db_session() as session:
            result = await session.execute(delete(BonusAnswerOption).where(BonusAnswerOption.bonus_question_id == bonus_question_id))
            await session.commit()
            return result.rowcount

    @staticmethod
    async def get_correct_answer(bonus_question_id: int) -> Optional[BonusAnswerOption]:
        """Получить правильный ответ для вопроса"""
        async with get_db_session() as session:
            result = await session.execute(
                select(BonusAnswerOption)
                .where(
                    BonusAnswerOption.bonus_question_id == bonus_question_id,
                    BonusAnswerOption.is_correct == True
                )
            )
            return result.scalar_one_or_none()

    @staticmethod
    async def get_count_by_bonus_question(bonus_question_id: int) -> int:
        """Получить количество вариантов ответов для вопроса"""
        async with get_db_session() as session:
            result = await session.execute(
                select(func.count(BonusAnswerOption.id))
                .where(BonusAnswerOption.bonus_question_id == bonus_question_id)
            )
            return result.scalar() or 0
