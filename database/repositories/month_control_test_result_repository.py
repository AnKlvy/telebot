"""
Репозиторий для работы с результатами контрольных тестов месяца
"""
from typing import List, Optional, Dict
from sqlalchemy import select, delete, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from ..models import (
    MonthControlTestResult, MonthControlQuestionResult, Student, MonthTest, 
    Question, Homework, Lesson, Group, MonthTestMicrotopic, User,
    MonthEntryTestResult, MonthEntryQuestionResult
)
from ..database import get_db_session
import random


class MonthControlTestResultRepository:
    """Репозиторий для работы с результатами контрольных тестов месяца"""
    
    @staticmethod
    async def get_all() -> List[MonthControlTestResult]:
        """Получить все результаты контрольных тестов месяца"""
        async with get_db_session() as session:
            result = await session.execute(
                select(MonthControlTestResult)
                .options(
                    selectinload(MonthControlTestResult.student).selectinload(Student.user),
                    selectinload(MonthControlTestResult.month_test),
                    selectinload(MonthControlTestResult.question_results)
                )
                .order_by(MonthControlTestResult.completed_at.desc())
            )
            return list(result.scalars().all())

    @staticmethod
    async def get_by_id(test_result_id: int) -> Optional[MonthControlTestResult]:
        """Получить результат контрольного теста по ID"""
        async with get_db_session() as session:
            result = await session.execute(
                select(MonthControlTestResult)
                .options(
                    selectinload(MonthControlTestResult.student).selectinload(Student.user),
                    selectinload(MonthControlTestResult.month_test).selectinload(MonthTest.subject),
                    selectinload(MonthControlTestResult.month_test).selectinload(MonthTest.course)
                )
                .where(MonthControlTestResult.id == test_result_id)
            )
            return result.scalar_one_or_none()

    @staticmethod
    async def get_by_student_and_month_test(student_id: int, month_test_id: int) -> Optional[MonthControlTestResult]:
        """Получить результат контрольного теста студента по тесту месяца"""
        async with get_db_session() as session:
            result = await session.execute(
                select(MonthControlTestResult)
                .options(
                    selectinload(MonthControlTestResult.student).selectinload(Student.user),
                    selectinload(MonthControlTestResult.month_test),
                    selectinload(MonthControlTestResult.question_results)
                )
                .where(
                    and_(
                        MonthControlTestResult.student_id == student_id,
                        MonthControlTestResult.month_test_id == month_test_id
                    )
                )
            )
            return result.scalar_one_or_none()

    @staticmethod
    async def has_student_taken_test(student_id: int, month_test_id: int) -> bool:
        """Проверить, проходил ли студент контрольный тест месяца"""
        result = await MonthControlTestResultRepository.get_by_student_and_month_test(student_id, month_test_id)
        return result is not None

    @staticmethod
    async def get_random_questions_for_month_test(month_test_id: int, questions_per_microtopic: int = 3) -> List[Dict]:
        """
        Получить случайные вопросы для контрольного теста месяца
        По каждой микротеме берется указанное количество случайных вопросов из ДЗ
        """
        async with get_db_session() as session:
            # Получаем тест месяца с микротемами
            month_test_result = await session.execute(
                select(MonthTest)
                .options(selectinload(MonthTest.microtopics))
                .where(MonthTest.id == month_test_id)
            )
            month_test = month_test_result.scalar_one_or_none()
            
            if not month_test:
                return []
            
            all_questions = []
            
            # Для каждой микротемы теста получаем случайные вопросы
            for microtopic_relation in month_test.microtopics:
                microtopic_number = microtopic_relation.microtopic_number
                
                # Получаем все вопросы по данной микротеме и предмету
                questions_result = await session.execute(
                    select(Question)
                    .options(selectinload(Question.answer_options))
                    .where(
                        and_(
                            Question.subject_id == month_test.subject_id,
                            Question.microtopic_number == microtopic_number
                        )
                    )
                )
                questions = list(questions_result.scalars().all())
                
                # Берем случайные вопросы (до указанного количества)
                if questions:
                    selected_count = min(questions_per_microtopic, len(questions))
                    selected_questions = random.sample(questions, selected_count)
                    
                    for question in selected_questions:
                        all_questions.append({
                            'question': question,
                            'microtopic_number': microtopic_number
                        })
            
            return all_questions

    @staticmethod
    async def create_test_result(student_id: int, month_test_id: int, 
                               question_results: List[Dict]) -> MonthControlTestResult:
        """Создать результат контрольного теста месяца"""
        async with get_db_session() as session:
            # Подсчитываем правильные ответы
            correct_answers = sum(1 for qr in question_results if qr['is_correct'])
            total_questions = len(question_results)
            score_percentage = int((correct_answers / total_questions) * 100) if total_questions > 0 else 0
            
            # Создаем основной результат
            test_result = MonthControlTestResult(
                student_id=student_id,
                month_test_id=month_test_id,
                total_questions=total_questions,
                correct_answers=correct_answers,
                score_percentage=score_percentage
            )
            session.add(test_result)
            await session.flush()  # Получаем ID
            
            # Создаем результаты ответов на вопросы
            for qr_data in question_results:
                question_result = MonthControlQuestionResult(
                    test_result_id=test_result.id,
                    question_id=qr_data['question_id'],
                    selected_answer_id=qr_data.get('selected_answer_id'),
                    is_correct=qr_data['is_correct'],
                    time_spent=qr_data.get('time_spent'),
                    microtopic_number=qr_data.get('microtopic_number')
                )
                session.add(question_result)
            
            await session.commit()
            await session.refresh(test_result)
            return test_result

    @staticmethod
    async def get_statistics_by_group_and_month_test(group_id: int, month_test_id: int) -> Dict:
        """Получить статистику контрольного теста месяца по группе и тесту"""
        async with get_db_session() as session:
            from ..models import student_groups
            
            # Получаем тест месяца
            month_test_result = await session.execute(
                select(MonthTest)
                .options(
                    selectinload(MonthTest.subject),
                    selectinload(MonthTest.course)
                )
                .where(MonthTest.id == month_test_id)
            )
            month_test = month_test_result.scalar_one_or_none()
            
            if not month_test:
                return {"completed": [], "not_completed": [], "month_test_name": "Неизвестный тест"}
            
            # Получаем группу
            group_result = await session.execute(
                select(Group)
                .options(selectinload(Group.subject))
                .where(Group.id == group_id)
            )
            group = group_result.scalar_one_or_none()
            
            if not group:
                return {"completed": [], "not_completed": [], "month_test_name": month_test.name}
            
            # Получаем всех студентов группы
            students_result = await session.execute(
                select(Student)
                .options(selectinload(Student.user))
                .join(student_groups, Student.id == student_groups.c.student_id)
                .where(student_groups.c.group_id == group_id)
            )
            all_students = list(students_result.scalars().all())
            
            # Получаем результаты тестов для студентов группы по данному тесту месяца
            test_results = await session.execute(
                select(MonthControlTestResult)
                .options(
                    selectinload(MonthControlTestResult.student).selectinload(Student.user),
                    selectinload(MonthControlTestResult.question_results)
                )
                .join(Student, MonthControlTestResult.student_id == Student.id)
                .join(student_groups, Student.id == student_groups.c.student_id)
                .where(
                    and_(
                        student_groups.c.group_id == group_id,
                        MonthControlTestResult.month_test_id == month_test_id
                    )
                )
            )
            completed_results = list(test_results.scalars().all())
            
            # Разделяем на прошедших и не прошедших тест
            completed_students = [result.student for result in completed_results]
            completed_student_ids = {student.id for student in completed_students}
            not_completed_students = [student for student in all_students if student.id not in completed_student_ids]
            
            return {
                "completed": completed_students,
                "not_completed": not_completed_students,
                "group_name": group.name,
                "subject_name": group.subject.name if group.subject else "Неизвестный предмет",
                "month_test_name": month_test.name,
                "test_results": completed_results
            }

    @staticmethod
    async def get_microtopic_statistics(test_result_id: int) -> Dict[int, Dict]:
        """Получить статистику по микротемам для результата контрольного теста"""
        async with get_db_session() as session:
            # Получаем результаты ответов с микротемами
            result = await session.execute(
                select(MonthControlQuestionResult)
                .where(MonthControlQuestionResult.test_result_id == test_result_id)
            )
            question_results = list(result.scalars().all())
            
            # Группируем по микротемам
            microtopic_stats = {}
            for qr in question_results:
                if qr.microtopic_number:
                    if qr.microtopic_number not in microtopic_stats:
                        microtopic_stats[qr.microtopic_number] = {
                            'total': 0,
                            'correct': 0,
                            'percentage': 0
                        }
                    
                    microtopic_stats[qr.microtopic_number]['total'] += 1
                    if qr.is_correct:
                        microtopic_stats[qr.microtopic_number]['correct'] += 1
            
            # Вычисляем проценты
            for microtopic_num, stats in microtopic_stats.items():
                if stats['total'] > 0:
                    stats['percentage'] = int((stats['correct'] / stats['total']) * 100)
            
            return microtopic_stats

    @staticmethod
    async def delete_by_id(test_result_id: int) -> bool:
        """Удалить результат контрольного теста месяца по ID"""
        async with get_db_session() as session:
            result = await session.execute(
                delete(MonthControlTestResult).where(MonthControlTestResult.id == test_result_id)
            )
            await session.commit()
            return result.rowcount > 0

    @staticmethod
    async def get_comparison_statistics(student_id: int, entry_test_id: int, control_test_id: int) -> Dict:
        """Получить сравнительную статистику входного и контрольного тестов"""
        async with get_db_session() as session:
            # Получаем результаты входного теста
            entry_result = await session.execute(
                select(MonthEntryTestResult)
                .options(selectinload(MonthEntryTestResult.question_results))
                .where(
                    and_(
                        MonthEntryTestResult.student_id == student_id,
                        MonthEntryTestResult.month_test_id == entry_test_id
                    )
                )
            )
            entry_test_result = entry_result.scalar_one_or_none()

            # Получаем результаты контрольного теста
            control_result = await session.execute(
                select(MonthControlTestResult)
                .options(selectinload(MonthControlTestResult.question_results))
                .where(
                    and_(
                        MonthControlTestResult.student_id == student_id,
                        MonthControlTestResult.month_test_id == control_test_id
                    )
                )
            )
            control_test_result = control_result.scalar_one_or_none()

            if not entry_test_result or not control_test_result:
                return {}

            # Получаем статистику по микротемам для входного теста
            from .month_entry_test_result_repository import MonthEntryTestResultRepository
            entry_microtopic_stats = await MonthEntryTestResultRepository.get_microtopic_statistics(entry_test_result.id)

            # Получаем статистику по микротемам для контрольного теста
            control_microtopic_stats = await MonthControlTestResultRepository.get_microtopic_statistics(control_test_result.id)

            # Сравниваем результаты
            comparison_data = {
                'entry_test': {
                    'correct_answers': entry_test_result.correct_answers,
                    'total_questions': entry_test_result.total_questions,
                    'score_percentage': entry_test_result.score_percentage,
                    'microtopic_stats': entry_microtopic_stats
                },
                'control_test': {
                    'correct_answers': control_test_result.correct_answers,
                    'total_questions': control_test_result.total_questions,
                    'score_percentage': control_test_result.score_percentage,
                    'microtopic_stats': control_microtopic_stats
                },
                'comparison': {
                    'score_difference': control_test_result.score_percentage - entry_test_result.score_percentage,
                    'microtopic_changes': {}
                }
            }

            # Сравниваем изменения по микротемам с новой формулой роста
            all_microtopics = set(entry_microtopic_stats.keys()) | set(control_microtopic_stats.keys())
            for microtopic_num in all_microtopics:
                entry_percentage = entry_microtopic_stats.get(microtopic_num, {}).get('percentage', 0)
                control_percentage = control_microtopic_stats.get(microtopic_num, {}).get('percentage', 0)

                # Рассчитываем рост по формуле: ((B - A) / A) × 100%
                if entry_percentage > 0:
                    growth_percentage = ((control_percentage - entry_percentage) / entry_percentage) * 100
                else:
                    # Если входной тест 0%, показываем абсолютный рост в процентных пунктах
                    growth_percentage = control_percentage  # Абсолютный рост = контрольный процент - 0
                    # Используем отрицательное значение как флаг для абсолютного роста
                    if growth_percentage > 0:
                        growth_percentage = -growth_percentage  # Отрицательное значение = абсолютный рост

                comparison_data['comparison']['microtopic_changes'][microtopic_num] = {
                    'entry_percentage': entry_percentage,
                    'control_percentage': control_percentage,
                    'difference': control_percentage - entry_percentage,
                    'growth_percentage': growth_percentage
                }

            return comparison_data
