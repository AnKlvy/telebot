from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any
import json
import logging
from ..database import get_db_session
from ..models import TrialEntResult, TrialEntQuestionResult, Student, User, Group, Subject, Question, AnswerOption

logger = logging.getLogger(__name__)


class TrialEntResultRepository:
    """Репозиторий для работы с результатами пробного ЕНТ"""

    @staticmethod
    async def create(
        student_id: int,
        required_subjects: List[str],
        profile_subjects: List[str],
        total_questions: int,
        correct_answers: int
    ) -> TrialEntResult:
        """Создать результат пробного ЕНТ"""
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"💾 TRIAL_ENT_REPO: Создаем результат для студента {student_id}")

        async with get_db_session() as session:
            try:
                trial_ent_result = TrialEntResult(
                    student_id=student_id,
                    required_subjects=json.dumps(required_subjects),
                    profile_subjects=json.dumps(profile_subjects),
                    total_questions=total_questions,
                    correct_answers=correct_answers
                )
                logger.info(f"📝 TRIAL_ENT_REPO: Объект создан, добавляем в сессию...")
                session.add(trial_ent_result)

                logger.info(f"💾 TRIAL_ENT_REPO: Коммитим изменения...")
                await session.commit()

                logger.info(f"🔄 TRIAL_ENT_REPO: Обновляем объект...")
                await session.refresh(trial_ent_result)

                logger.info(f"✅ TRIAL_ENT_REPO: Результат создан с ID {trial_ent_result.id}")
                return trial_ent_result

            except Exception as e:
                logger.error(f"❌ TRIAL_ENT_REPO: Ошибка при создании результата: {e}")
                await session.rollback()
                raise

    @staticmethod
    async def get_by_id(trial_ent_result_id: int) -> Optional[TrialEntResult]:
        """Получить результат пробного ЕНТ по ID"""
        async with get_db_session() as session:
            result = await session.execute(
                select(TrialEntResult)
                .options(selectinload(TrialEntResult.student).selectinload(Student.user))
                .where(TrialEntResult.id == trial_ent_result_id)
            )
            return result.scalar_one_or_none()

    @staticmethod
    async def get_by_student(student_id: int, limit: int = 10) -> List[TrialEntResult]:
        """Получить результаты пробного ЕНТ студента (последние limit результатов)"""
        async with get_db_session() as session:
            result = await session.execute(
                select(TrialEntResult)
                .options(selectinload(TrialEntResult.student).selectinload(Student.user))
                .where(TrialEntResult.student_id == student_id)
                .order_by(desc(TrialEntResult.completed_at))
                .limit(limit)
            )
            return result.scalars().all()

    @staticmethod
    async def get_latest_by_student(student_id: int) -> Optional[TrialEntResult]:
        """Получить последний результат пробного ЕНТ студента"""
        async with get_db_session() as session:
            result = await session.execute(
                select(TrialEntResult)
                .options(selectinload(TrialEntResult.student).selectinload(Student.user))
                .where(TrialEntResult.student_id == student_id)
                .order_by(desc(TrialEntResult.completed_at))
                .limit(1)
            )
            return result.scalar_one_or_none()

    @staticmethod
    async def get_students_with_results_by_group(group_id: int) -> List[Dict[str, Any]]:
        """Получить студентов группы с их результатами пробного ЕНТ"""
        async with get_db_session() as session:
            # Получаем всех студентов группы
            students_result = await session.execute(
                select(Student)
                .options(selectinload(Student.user))
                .join(Student.groups)
                .where(Group.id == group_id)
            )
            students = students_result.scalars().all()

            students_data = []
            for student in students:
                # Получаем последний результат пробного ЕНТ для каждого студента
                latest_result = await TrialEntResultRepository.get_latest_by_student(student.id)
                
                students_data.append({
                    'student': student,
                    'latest_result': latest_result,
                    'has_results': latest_result is not None
                })

            return students_data

    @staticmethod
    async def get_statistics_by_group(group_id: int) -> Dict[str, Any]:
        """Получить статистику пробного ЕНТ по группе"""
        students_data = await TrialEntResultRepository.get_students_with_results_by_group(group_id)
        
        completed_students = []
        not_completed_students = []
        test_results = []

        for student_data in students_data:
            student = student_data['student']
            latest_result = student_data['latest_result']
            
            if latest_result:
                completed_students.append(student)
                test_results.append(latest_result)
            else:
                not_completed_students.append(student)

        # Получаем информацию о группе
        async with get_db_session() as session:
            group_result = await session.execute(
                select(Group)
                .options(selectinload(Group.subject))
                .where(Group.id == group_id)
            )
            group = group_result.scalar_one_or_none()

        return {
            'group_name': group.name if group else 'Неизвестная группа',
            'completed': completed_students,
            'not_completed': not_completed_students,
            'test_results': test_results
        }

    @staticmethod
    async def get_microtopic_statistics(trial_ent_result_id: int) -> Dict[int, Dict[str, Any]]:
        """Получить статистику по микротемам для результата пробного ЕНТ"""
        async with get_db_session() as session:
            # Получаем все результаты вопросов для данного теста
            result = await session.execute(
                select(TrialEntQuestionResult)
                .where(TrialEntQuestionResult.test_result_id == trial_ent_result_id)
            )
            question_results = result.scalars().all()

            # Группируем по микротемам
            microtopic_stats = {}
            for qr in question_results:
                microtopic_num = qr.microtopic_number
                # Пропускаем вопросы без микротемы
                if microtopic_num is None:
                    continue

                if microtopic_num not in microtopic_stats:
                    microtopic_stats[microtopic_num] = {
                        'correct': 0,
                        'total': 0,
                        'percentage': 0
                    }

                microtopic_stats[microtopic_num]['total'] += 1
                if qr.is_correct:
                    microtopic_stats[microtopic_num]['correct'] += 1

            # Вычисляем проценты
            for microtopic_num in microtopic_stats:
                stats = microtopic_stats[microtopic_num]
                if stats['total'] > 0:
                    stats['percentage'] = round((stats['correct'] / stats['total']) * 100)

            return microtopic_stats

    @staticmethod
    async def get_subject_statistics(trial_ent_result_id: int) -> Dict[str, Dict[str, Any]]:
        """Получить статистику по предметам для результата пробного ЕНТ"""
        async with get_db_session() as session:
            # Получаем все результаты вопросов для данного теста
            result = await session.execute(
                select(TrialEntQuestionResult)
                .where(TrialEntQuestionResult.test_result_id == trial_ent_result_id)
            )
            question_results = result.scalars().all()

            # Группируем по предметам
            subject_stats = {}
            for qr in question_results:
                subject_code = qr.subject_code
                if subject_code not in subject_stats:
                    subject_stats[subject_code] = {
                        'correct': 0,
                        'total': 0,
                        'percentage': 0
                    }
                
                subject_stats[subject_code]['total'] += 1
                if qr.is_correct:
                    subject_stats[subject_code]['correct'] += 1

            # Вычисляем проценты
            for subject_code in subject_stats:
                stats = subject_stats[subject_code]
                if stats['total'] > 0:
                    stats['percentage'] = round((stats['correct'] / stats['total']) * 100)

            return subject_stats

    @staticmethod
    async def delete_by_id(trial_ent_result_id: int) -> bool:
        """Удалить результат пробного ЕНТ по ID"""
        async with get_db_session() as session:
            result = await session.execute(
                select(TrialEntResult).where(TrialEntResult.id == trial_ent_result_id)
            )
            trial_ent_result = result.scalar_one_or_none()
            
            if trial_ent_result:
                await session.delete(trial_ent_result)
                await session.commit()
                return True
            return False

    @staticmethod
    async def get_all() -> List[TrialEntResult]:
        """Получить все результаты пробного ЕНТ"""
        async with get_db_session() as session:
            result = await session.execute(
                select(TrialEntResult)
                .options(selectinload(TrialEntResult.student).selectinload(Student.user))
                .order_by(desc(TrialEntResult.completed_at))
            )
            return result.scalars().all()
