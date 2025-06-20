from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, Integer
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any
import logging
from ..database import get_db_session
from ..models import TrialEntQuestionResult, TrialEntResult, Question, AnswerOption

logger = logging.getLogger(__name__)


class TrialEntQuestionResultRepository:
    """Репозиторий для работы с результатами вопросов пробного ЕНТ"""

    @staticmethod
    async def create(
        test_result_id: int,
        question_id: int,
        selected_answer_id: Optional[int],
        is_correct: bool,
        subject_code: str,
        time_spent: Optional[int] = None,
        microtopic_number: Optional[int] = None
    ) -> TrialEntQuestionResult:
        """Создать результат ответа на вопрос пробного ЕНТ"""
        async with get_db_session() as session:
            question_result = TrialEntQuestionResult(
                test_result_id=test_result_id,
                question_id=question_id,
                selected_answer_id=selected_answer_id,
                is_correct=is_correct,
                subject_code=subject_code,
                time_spent=time_spent,
                microtopic_number=microtopic_number
            )
            session.add(question_result)
            await session.commit()
            await session.refresh(question_result)
            return question_result

    @staticmethod
    async def create_batch(question_results_data: List[Dict[str, Any]]) -> List[TrialEntQuestionResult]:
        """Создать несколько результатов вопросов пробного ЕНТ за один раз"""
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"📊 TRIAL_ENT_QUESTION_REPO: Создаем {len(question_results_data)} результатов вопросов")

        async with get_db_session() as session:
            try:
                question_results = []
                for i, data in enumerate(question_results_data):
                    question_result = TrialEntQuestionResult(**data)
                    session.add(question_result)
                    question_results.append(question_result)

                    if i % 50 == 0:  # Логируем каждые 50 записей
                        logger.info(f"📝 TRIAL_ENT_QUESTION_REPO: Добавлено {i+1}/{len(question_results_data)} записей")

                logger.info(f"💾 TRIAL_ENT_QUESTION_REPO: Коммитим {len(question_results)} записей...")
                await session.commit()

                logger.info(f"🔄 TRIAL_ENT_QUESTION_REPO: Обновляем объекты...")
                # Обновляем объекты после коммита
                for qr in question_results:
                    await session.refresh(qr)

                logger.info(f"✅ TRIAL_ENT_QUESTION_REPO: Создано {len(question_results)} результатов вопросов")
                return question_results

            except Exception as e:
                logger.error(f"❌ TRIAL_ENT_QUESTION_REPO: Ошибка при создании результатов: {e}")
                await session.rollback()
                raise

    @staticmethod
    async def get_by_id(question_result_id: int) -> Optional[TrialEntQuestionResult]:
        """Получить результат вопроса пробного ЕНТ по ID"""
        async with get_db_session() as session:
            result = await session.execute(
                select(TrialEntQuestionResult)
                .options(
                    selectinload(TrialEntQuestionResult.test_result),
                    selectinload(TrialEntQuestionResult.question),
                    selectinload(TrialEntQuestionResult.selected_answer)
                )
                .where(TrialEntQuestionResult.id == question_result_id)
            )
            return result.scalar_one_or_none()

    @staticmethod
    async def get_by_test_result(test_result_id: int) -> List[TrialEntQuestionResult]:
        """Получить все результаты вопросов для конкретного результата пробного ЕНТ"""
        async with get_db_session() as session:
            result = await session.execute(
                select(TrialEntQuestionResult)
                .options(
                    selectinload(TrialEntQuestionResult.question),
                    selectinload(TrialEntQuestionResult.selected_answer)
                )
                .where(TrialEntQuestionResult.test_result_id == test_result_id)
                .order_by(TrialEntQuestionResult.id)
            )
            return result.scalars().all()

    @staticmethod
    async def get_by_test_result_and_subject(test_result_id: int, subject_code: str) -> List[TrialEntQuestionResult]:
        """Получить результаты вопросов для конкретного предмета в тесте"""
        async with get_db_session() as session:
            result = await session.execute(
                select(TrialEntQuestionResult)
                .options(
                    selectinload(TrialEntQuestionResult.question),
                    selectinload(TrialEntQuestionResult.selected_answer)
                )
                .where(
                    and_(
                        TrialEntQuestionResult.test_result_id == test_result_id,
                        TrialEntQuestionResult.subject_code == subject_code
                    )
                )
                .order_by(TrialEntQuestionResult.id)
            )
            return result.scalars().all()

    @staticmethod
    async def get_by_test_result_and_microtopic(
        test_result_id: int, 
        microtopic_number: int
    ) -> List[TrialEntQuestionResult]:
        """Получить результаты вопросов для конкретной микротемы в тесте"""
        async with get_db_session() as session:
            result = await session.execute(
                select(TrialEntQuestionResult)
                .options(
                    selectinload(TrialEntQuestionResult.question),
                    selectinload(TrialEntQuestionResult.selected_answer)
                )
                .where(
                    and_(
                        TrialEntQuestionResult.test_result_id == test_result_id,
                        TrialEntQuestionResult.microtopic_number == microtopic_number
                    )
                )
                .order_by(TrialEntQuestionResult.id)
            )
            return result.scalars().all()

    @staticmethod
    async def get_statistics_by_subject(test_result_id: int) -> Dict[str, Dict[str, Any]]:
        """Получить статистику по предметам для результата пробного ЕНТ"""
        async with get_db_session() as session:
            result = await session.execute(
                select(
                    TrialEntQuestionResult.subject_code,
                    func.count(TrialEntQuestionResult.id).label('total'),
                    func.sum(func.cast(TrialEntQuestionResult.is_correct, Integer)).label('correct')
                )
                .where(TrialEntQuestionResult.test_result_id == test_result_id)
                .group_by(TrialEntQuestionResult.subject_code)
            )
            
            statistics = {}
            for row in result:
                subject_code = row.subject_code
                total = row.total
                correct = row.correct or 0
                percentage = round((correct / total) * 100) if total > 0 else 0
                
                statistics[subject_code] = {
                    'total': total,
                    'correct': correct,
                    'percentage': percentage
                }
            
            return statistics

    @staticmethod
    async def get_statistics_by_microtopic(test_result_id: int) -> Dict[int, Dict[str, Any]]:
        """Получить статистику по микротемам для результата пробного ЕНТ"""
        async with get_db_session() as session:
            result = await session.execute(
                select(
                    TrialEntQuestionResult.microtopic_number,
                    func.count(TrialEntQuestionResult.id).label('total'),
                    func.sum(func.cast(TrialEntQuestionResult.is_correct, Integer)).label('correct')
                )
                .where(TrialEntQuestionResult.test_result_id == test_result_id)
                .group_by(TrialEntQuestionResult.microtopic_number)
            )
            
            statistics = {}
            for row in result:
                microtopic_number = row.microtopic_number
                # Пропускаем строки с NULL microtopic_number
                if microtopic_number is None:
                    continue

                total = row.total
                correct = row.correct or 0
                percentage = round((correct / total) * 100) if total > 0 else 0

                statistics[microtopic_number] = {
                    'total': total,
                    'correct': correct,
                    'percentage': percentage
                }

            return statistics

    @staticmethod
    async def delete_by_test_result(test_result_id: int) -> bool:
        """Удалить все результаты вопросов для конкретного результата пробного ЕНТ"""
        async with get_db_session() as session:
            result = await session.execute(
                select(TrialEntQuestionResult)
                .where(TrialEntQuestionResult.test_result_id == test_result_id)
            )
            question_results = result.scalars().all()
            
            if question_results:
                for qr in question_results:
                    await session.delete(qr)
                await session.commit()
                return True
            return False

    @staticmethod
    async def delete_by_id(question_result_id: int) -> bool:
        """Удалить результат вопроса пробного ЕНТ по ID"""
        async with get_db_session() as session:
            result = await session.execute(
                select(TrialEntQuestionResult)
                .where(TrialEntQuestionResult.id == question_result_id)
            )
            question_result = result.scalar_one_or_none()
            
            if question_result:
                await session.delete(question_result)
                await session.commit()
                return True
            return False

    @staticmethod
    async def get_all() -> List[TrialEntQuestionResult]:
        """Получить все результаты вопросов пробного ЕНТ"""
        async with get_db_session() as session:
            result = await session.execute(
                select(TrialEntQuestionResult)
                .options(
                    selectinload(TrialEntQuestionResult.test_result),
                    selectinload(TrialEntQuestionResult.question),
                    selectinload(TrialEntQuestionResult.selected_answer)
                )
                .order_by(TrialEntQuestionResult.created_at)
            )
            return result.scalars().all()
