"""
Репозиторий для работы с вариантами ответов
"""
from typing import List, Optional
from sqlalchemy import select, delete, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from ..models import AnswerOption, Question
from ..database import get_db_session


class AnswerOptionRepository:
    """Репозиторий для работы с вариантами ответов"""
    
    @staticmethod
    async def get_all() -> List[AnswerOption]:
        """Получить все варианты ответов"""
        async with get_db_session() as session:
            result = await session.execute(
                select(AnswerOption)
                .options(selectinload(AnswerOption.question))
                .order_by(AnswerOption.question_id, AnswerOption.order_number)
            )
            return list(result.scalars().all())

    @staticmethod
    async def get_by_id(option_id: int) -> Optional[AnswerOption]:
        """Получить вариант ответа по ID"""
        async with get_db_session() as session:
            result = await session.execute(
                select(AnswerOption)
                .options(selectinload(AnswerOption.question))
                .where(AnswerOption.id == option_id)
            )
            return result.scalar_one_or_none()

    @staticmethod
    async def get_by_question(question_id: int) -> List[AnswerOption]:
        """Получить все варианты ответов для вопроса"""
        async with get_db_session() as session:
            result = await session.execute(
                select(AnswerOption)
                .options(selectinload(AnswerOption.question))
                .where(AnswerOption.question_id == question_id)
                .order_by(AnswerOption.order_number)
            )
            return list(result.scalars().all())

    @staticmethod
    async def get_correct_answers(question_id: int) -> List[AnswerOption]:
        """Получить правильные ответы для вопроса"""
        async with get_db_session() as session:
            result = await session.execute(
                select(AnswerOption)
                .options(selectinload(AnswerOption.question))
                .where(
                    AnswerOption.question_id == question_id,
                    AnswerOption.is_correct == True
                )
                .order_by(AnswerOption.order_number)
            )
            return list(result.scalars().all())

    @staticmethod
    async def get_next_order_number(question_id: int) -> int:
        """Получить следующий порядковый номер для варианта ответа"""
        async with get_db_session() as session:
            result = await session.execute(
                select(func.max(AnswerOption.order_number))
                .where(AnswerOption.question_id == question_id)
            )
            max_order = result.scalar()
            return (max_order or 0) + 1

    @staticmethod
    async def create(question_id: int, text: str, is_correct: bool = False) -> AnswerOption:
        """Создать новый вариант ответа"""
        async with get_db_session() as session:
            # Проверяем существование вопроса
            question_exists = await session.execute(
                select(Question).where(Question.id == question_id)
            )
            if not question_exists.scalar_one_or_none():
                raise ValueError(f"Вопрос с ID {question_id} не найден")

            # Получаем следующий порядковый номер
            order_number = await AnswerOptionRepository.get_next_order_number(question_id)

            answer_option = AnswerOption(
                question_id=question_id,
                text=text,
                is_correct=is_correct,
                order_number=order_number
            )
            session.add(answer_option)
            await session.commit()
            await session.refresh(answer_option)
            return answer_option

    @staticmethod
    async def create_multiple(question_id: int, options_data: List[dict]) -> List[AnswerOption]:
        """
        Создать несколько вариантов ответов для вопроса
        options_data: список словарей с ключами 'text' и 'is_correct'
        """
        async with get_db_session() as session:
            # Проверяем существование вопроса
            question_exists = await session.execute(
                select(Question).where(Question.id == question_id)
            )
            if not question_exists.scalar_one_or_none():
                raise ValueError(f"Вопрос с ID {question_id} не найден")

            # Удаляем существующие варианты ответов
            await session.execute(
                delete(AnswerOption).where(AnswerOption.question_id == question_id)
            )

            # Создаем новые варианты ответов
            created_options = []
            for i, option_data in enumerate(options_data, 1):
                answer_option = AnswerOption(
                    question_id=question_id,
                    text=option_data['text'],
                    is_correct=option_data.get('is_correct', False),
                    order_number=i
                )
                session.add(answer_option)
                created_options.append(answer_option)

            await session.commit()
            
            # Обновляем объекты после коммита
            for option in created_options:
                await session.refresh(option)
            
            return created_options

    @staticmethod
    async def update(option_id: int, **kwargs) -> Optional[AnswerOption]:
        """Обновить вариант ответа"""
        async with get_db_session() as session:
            option = await session.get(AnswerOption, option_id)
            if not option:
                return None

            for key, value in kwargs.items():
                if hasattr(option, key):
                    setattr(option, key, value)

            await session.commit()
            await session.refresh(option)
            return option

    @staticmethod
    async def delete(option_id: int) -> bool:
        """Удалить вариант ответа"""
        async with get_db_session() as session:
            # Получаем информацию о варианте перед удалением
            option = await session.get(AnswerOption, option_id)
            if not option:
                return False

            question_id = option.question_id
            order_number = option.order_number

            # Удаляем вариант ответа
            result = await session.execute(
                delete(AnswerOption).where(AnswerOption.id == option_id)
            )
            
            # Перенумеровываем оставшиеся варианты
            await session.execute(
                update(AnswerOption)
                .where(
                    AnswerOption.question_id == question_id,
                    AnswerOption.order_number > order_number
                )
                .values(order_number=AnswerOption.order_number - 1)
            )
            
            await session.commit()
            return result.rowcount > 0

    @staticmethod
    async def delete_by_question(question_id: int) -> bool:
        """Удалить все варианты ответов для вопроса"""
        async with get_db_session() as session:
            result = await session.execute(
                delete(AnswerOption).where(AnswerOption.question_id == question_id)
            )
            await session.commit()
            return result.rowcount > 0

    @staticmethod
    async def set_correct_answer(question_id: int, option_id: int) -> bool:
        """Установить правильный ответ (сбросить все остальные)"""
        async with get_db_session() as session:
            # Сбрасываем все правильные ответы для вопроса
            await session.execute(
                update(AnswerOption)
                .where(AnswerOption.question_id == question_id)
                .values(is_correct=False)
            )
            
            # Устанавливаем правильный ответ
            result = await session.execute(
                update(AnswerOption)
                .where(
                    AnswerOption.id == option_id,
                    AnswerOption.question_id == question_id
                )
                .values(is_correct=True)
            )
            
            await session.commit()
            return result.rowcount > 0

    @staticmethod
    async def set_multiple_correct_answers(question_id: int, option_ids: List[int]) -> bool:
        """Установить несколько правильных ответов"""
        async with get_db_session() as session:
            # Сбрасываем все правильные ответы для вопроса
            await session.execute(
                update(AnswerOption)
                .where(AnswerOption.question_id == question_id)
                .values(is_correct=False)
            )
            
            # Устанавливаем правильные ответы
            if option_ids:
                await session.execute(
                    update(AnswerOption)
                    .where(
                        AnswerOption.id.in_(option_ids),
                        AnswerOption.question_id == question_id
                    )
                    .values(is_correct=True)
                )
            
            await session.commit()
            return True

    @staticmethod
    async def get_options_count(question_id: int) -> int:
        """Получить количество вариантов ответов для вопроса"""
        async with get_db_session() as session:
            result = await session.execute(
                select(func.count(AnswerOption.id))
                .where(AnswerOption.question_id == question_id)
            )
            return result.scalar() or 0

    @staticmethod
    async def reorder_options(question_id: int, option_orders: List[tuple]) -> bool:
        """
        Изменить порядок вариантов ответов
        option_orders: список кортежей (option_id, new_order_number)
        """
        async with get_db_session() as session:
            try:
                for option_id, new_order in option_orders:
                    await session.execute(
                        update(AnswerOption)
                        .where(
                            AnswerOption.id == option_id,
                            AnswerOption.question_id == question_id
                        )
                        .values(order_number=new_order)
                    )
                await session.commit()
                return True
            except Exception:
                await session.rollback()
                return False
