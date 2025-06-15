"""
Репозиторий для работы с вопросами домашних заданий
"""
from typing import List, Optional, Type
from sqlalchemy import select, delete, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from ..models import Question, AnswerOption, Homework, Microtopic, Subject
from ..database import get_db_session
from .base_question_repository import BaseQuestionRepository


class QuestionRepository(BaseQuestionRepository):
    """Репозиторий для работы с вопросами домашних заданий"""

    # Реализация абстрактных свойств базового класса
    @property
    def question_model(self) -> Type:
        return Question

    @property
    def answer_option_model(self) -> Type:
        return AnswerOption

    @property
    def parent_id_field(self) -> str:
        return 'homework_id'

    @property
    def parent_model(self) -> Type:
        return Homework

    # Специфичные методы для домашних заданий
    async def create(self, homework_id: int, text: str, subject_id: int, microtopic_number: Optional[int] = None,
                    photo_path: Optional[str] = None, time_limit: int = 30) -> Question:
        """Создать новый вопрос для домашнего задания"""
        async with get_db_session() as session:
            # Проверяем существование предмета
            subject_exists = await session.execute(
                select(Subject).where(Subject.id == subject_id)
            )
            if not subject_exists.scalar_one_or_none():
                raise ValueError(f"Предмет с ID {subject_id} не найден")

            # Проверяем существование микротемы (если указана)
            if microtopic_number:
                microtopic_exists = await session.execute(
                    select(Microtopic).where(
                        Microtopic.subject_id == subject_id,
                        Microtopic.number == microtopic_number
                    )
                )
                if not microtopic_exists.scalar_one_or_none():
                    raise ValueError(f"Микротема с номером {microtopic_number} не найдена для предмета с ID {subject_id}")

            # Используем базовый метод создания с дополнительными параметрами
            return await self.create_question(
                parent_id=homework_id,
                text=text,
                photo_path=photo_path,
                time_limit=time_limit,
                subject_id=subject_id,
                microtopic_number=microtopic_number
            )

    # Переопределяем методы базового класса для добавления специфичной логики
    async def get_all(self) -> List[Question]:
        """Получить все вопросы с дополнительными связями"""
        async with get_db_session() as session:
            result = await session.execute(
                select(Question)
                .options(
                    selectinload(Question.homework),
                    selectinload(Question.subject),
                    selectinload(Question.answer_options)
                )
                .order_by(Question.homework_id, Question.order_number)
            )
            return list(result.scalars().all())

    async def get_by_id(self, question_id: int) -> Optional[Question]:
        """Получить вопрос по ID с дополнительными связями"""
        async with get_db_session() as session:
            result = await session.execute(
                select(Question)
                .options(
                    selectinload(Question.homework),
                    selectinload(Question.subject),
                    selectinload(Question.answer_options)
                )
                .where(Question.id == question_id)
            )
            return result.scalar_one_or_none()

    async def get_by_homework(self, homework_id: int) -> List[Question]:
        """Получить все вопросы домашнего задания"""
        return await self.get_by_parent(homework_id)

    async def get_next_order_number(self, homework_id: int) -> int:
        """Получить следующий порядковый номер для вопроса в ДЗ"""
        return await super().get_next_order_number(homework_id)



    @staticmethod
    async def update(question_id: int, **kwargs) -> Optional[Question]:
        """Обновить вопрос"""
        async with get_db_session() as session:
            question = await session.get(Question, question_id)
            if not question:
                return None

            # Проверяем существование микротемы при изменении
            if 'microtopic_number' in kwargs and kwargs['microtopic_number'] and 'subject_id' in kwargs:
                microtopic_exists = await session.execute(
                    select(Microtopic).where(
                        Microtopic.subject_id == kwargs['subject_id'],
                        Microtopic.number == kwargs['microtopic_number']
                    )
                )
                if not microtopic_exists.scalar_one_or_none():
                    raise ValueError(f"Микротема с номером {kwargs['microtopic_number']} не найдена для предмета с ID {kwargs['subject_id']}")

            for key, value in kwargs.items():
                if hasattr(question, key):
                    setattr(question, key, value)

            await session.commit()
            await session.refresh(question)
            return question

    @staticmethod
    async def delete(question_id: int) -> bool:
        """Удалить вопрос"""
        async with get_db_session() as session:
            # Получаем информацию о вопросе перед удалением
            question = await session.get(Question, question_id)
            if not question:
                return False

            homework_id = question.homework_id
            order_number = question.order_number

            # Удаляем вопрос
            result = await session.execute(
                delete(Question).where(Question.id == question_id)
            )
            
            # Перенумеровываем оставшиеся вопросы
            await session.execute(
                update(Question)
                .where(
                    Question.homework_id == homework_id,
                    Question.order_number > order_number
                )
                .values(order_number=Question.order_number - 1)
            )
            
            await session.commit()
            return result.rowcount > 0

    @staticmethod
    async def reorder_questions(homework_id: int, question_orders: List[tuple]) -> bool:
        """
        Изменить порядок вопросов в ДЗ
        question_orders: список кортежей (question_id, new_order_number)
        """
        async with get_db_session() as session:
            try:
                for question_id, new_order in question_orders:
                    await session.execute(
                        update(Question)
                        .where(
                            Question.id == question_id,
                            Question.homework_id == homework_id
                        )
                        .values(order_number=new_order)
                    )
                await session.commit()
                return True
            except Exception:
                await session.rollback()
                return False

    @staticmethod
    async def get_questions_count(homework_id: int) -> int:
        """Получить количество вопросов в ДЗ"""
        async with get_db_session() as session:
            result = await session.execute(
                select(func.count(Question.id))
                .where(Question.homework_id == homework_id)
            )
            return result.scalar() or 0

    @staticmethod
    async def move_question_up(question_id: int) -> bool:
        """Переместить вопрос вверх (уменьшить order_number)"""
        async with get_db_session() as session:
            question = await session.get(Question, question_id)
            if not question or question.order_number <= 1:
                return False

            # Находим вопрос, который нужно поменять местами
            prev_question = await session.execute(
                select(Question)
                .where(
                    Question.homework_id == question.homework_id,
                    Question.order_number == question.order_number - 1
                )
            )
            prev_question = prev_question.scalar_one_or_none()
            
            if not prev_question:
                return False

            # Меняем местами
            question.order_number, prev_question.order_number = prev_question.order_number, question.order_number
            
            await session.commit()
            return True

    @staticmethod
    async def move_question_down(question_id: int) -> bool:
        """Переместить вопрос вниз (увеличить order_number)"""
        async with get_db_session() as session:
            question = await session.get(Question, question_id)
            if not question:
                return False

            # Находим вопрос, который нужно поменять местами
            next_question = await session.execute(
                select(Question)
                .where(
                    Question.homework_id == question.homework_id,
                    Question.order_number == question.order_number + 1
                )
            )
            next_question = next_question.scalar_one_or_none()
            
            if not next_question:
                return False

            # Меняем местами
            question.order_number, next_question.order_number = next_question.order_number, question.order_number
            
            await session.commit()
            return True
