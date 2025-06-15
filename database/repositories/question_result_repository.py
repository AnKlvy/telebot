"""
Репозиторий для работы с результатами ответов на вопросы
"""
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from ..database import get_db_session
from ..models import QuestionResult, HomeworkResult, Question, AnswerOption


class QuestionResultRepository:
    """Репозиторий для работы с результатами ответов на вопросы"""

    @staticmethod
    async def create(homework_result_id: int, question_id: int, selected_answer_id: int = None,
                    is_correct: bool = False, time_spent: int = None, 
                    microtopic_number: int = None) -> QuestionResult:
        """Создать результат ответа на вопрос"""
        async with get_db_session() as session:
            question_result = QuestionResult(
                homework_result_id=homework_result_id,
                question_id=question_id,
                selected_answer_id=selected_answer_id,
                is_correct=is_correct,
                time_spent=time_spent,
                microtopic_number=microtopic_number
            )
            session.add(question_result)
            await session.commit()
            await session.refresh(question_result)
            return question_result

    @staticmethod
    async def create_multiple(homework_result_id: int, question_results: list[dict]) -> list[QuestionResult]:
        """Создать несколько результатов ответов"""
        async with get_db_session() as session:
            results = []
            for qr_data in question_results:
                question_result = QuestionResult(
                    homework_result_id=homework_result_id,
                    question_id=qr_data['question_id'],
                    selected_answer_id=qr_data.get('selected_answer_id'),
                    is_correct=qr_data['is_correct'],
                    time_spent=qr_data.get('time_spent'),
                    microtopic_number=qr_data.get('microtopic_number')
                )
                session.add(question_result)
                results.append(question_result)
            
            await session.commit()
            for result in results:
                await session.refresh(result)
            return results

    @staticmethod
    async def get_by_id(question_result_id: int) -> QuestionResult:
        """Получить результат по ID"""
        async with get_db_session() as session:
            result = await session.execute(
                select(QuestionResult)
                .options(
                    selectinload(QuestionResult.question),
                    selectinload(QuestionResult.selected_answer),
                    selectinload(QuestionResult.homework_result)
                )
                .where(QuestionResult.id == question_result_id)
            )
            return result.scalar_one_or_none()

    @staticmethod
    async def get_by_homework_result(homework_result_id: int) -> list[QuestionResult]:
        """Получить все результаты ответов по результату ДЗ"""
        async with get_db_session() as session:
            result = await session.execute(
                select(QuestionResult)
                .options(
                    selectinload(QuestionResult.question),
                    selectinload(QuestionResult.selected_answer)
                )
                .where(QuestionResult.homework_result_id == homework_result_id)
                .order_by(QuestionResult.created_at.asc())
            )
            return result.scalars().all()

    @staticmethod
    async def get_by_question(question_id: int) -> list[QuestionResult]:
        """Получить все результаты по вопросу"""
        async with get_db_session() as session:
            result = await session.execute(
                select(QuestionResult)
                .options(selectinload(QuestionResult.homework_result))
                .where(QuestionResult.question_id == question_id)
                .order_by(QuestionResult.created_at.desc())
            )
            return result.scalars().all()

    @staticmethod
    async def get_student_question_history(student_id: int, question_id: int) -> list[QuestionResult]:
        """Получить историю ответов студента на конкретный вопрос"""
        async with get_db_session() as session:
            result = await session.execute(
                select(QuestionResult)
                .join(HomeworkResult, QuestionResult.homework_result_id == HomeworkResult.id)
                .where(and_(
                    HomeworkResult.student_id == student_id,
                    QuestionResult.question_id == question_id
                ))
                .order_by(QuestionResult.created_at.asc())
            )
            return result.scalars().all()

    @staticmethod
    async def update(question_result_id: int, **kwargs) -> QuestionResult:
        """Обновить результат ответа"""
        async with get_db_session() as session:
            result = await session.execute(
                select(QuestionResult).where(QuestionResult.id == question_result_id)
            )
            question_result = result.scalar_one_or_none()
            
            if question_result:
                for key, value in kwargs.items():
                    if hasattr(question_result, key):
                        setattr(question_result, key, value)
                
                await session.commit()
                await session.refresh(question_result)
            
            return question_result

    @staticmethod
    async def delete(question_result_id: int) -> bool:
        """Удалить результат ответа"""
        async with get_db_session() as session:
            result = await session.execute(
                select(QuestionResult).where(QuestionResult.id == question_result_id)
            )
            question_result = result.scalar_one_or_none()
            
            if question_result:
                await session.delete(question_result)
                await session.commit()
                return True
            return False

    @staticmethod
    async def get_all() -> list[QuestionResult]:
        """Получить все результаты ответов"""
        async with get_db_session() as session:
            result = await session.execute(
                select(QuestionResult)
                .options(
                    selectinload(QuestionResult.question),
                    selectinload(QuestionResult.selected_answer),
                    selectinload(QuestionResult.homework_result)
                )
                .order_by(QuestionResult.created_at.desc())
            )
            return result.scalars().all()
