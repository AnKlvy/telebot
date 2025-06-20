"""
Репозиторий для работы с результатами входных тестов курса
"""
from typing import List, Optional, Dict
from sqlalchemy import select, delete, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from ..models import (
    CourseEntryTestResult, CourseEntryQuestionResult, Student, Subject, User, 
    Question, Homework, Lesson, Group
)
from ..database import get_db_session
import random


class CourseEntryTestResultRepository:
    """Репозиторий для работы с результатами входных тестов курса"""
    
    @staticmethod
    async def get_all() -> List[CourseEntryTestResult]:
        """Получить все результаты входных тестов курса"""
        async with get_db_session() as session:
            result = await session.execute(
                select(CourseEntryTestResult)
                .options(
                    selectinload(CourseEntryTestResult.student).selectinload(Student.user),
                    selectinload(CourseEntryTestResult.subject),
                    selectinload(CourseEntryTestResult.question_results)
                )
                .order_by(CourseEntryTestResult.completed_at.desc())
            )
            return list(result.scalars().all())

    @staticmethod
    async def get_by_id(test_result_id: int) -> Optional[CourseEntryTestResult]:
        """Получить результат теста по ID"""
        async with get_db_session() as session:
            result = await session.execute(
                select(CourseEntryTestResult)
                .options(
                    selectinload(CourseEntryTestResult.student).selectinload(Student.user),
                    selectinload(CourseEntryTestResult.subject),
                    selectinload(CourseEntryTestResult.question_results)
                )
                .where(CourseEntryTestResult.id == test_result_id)
            )
            return result.scalar_one_or_none()

    @staticmethod
    async def get_by_student_and_subject(student_id: int, subject_id: int) -> Optional[CourseEntryTestResult]:
        """Получить результат теста студента по предмету"""
        async with get_db_session() as session:
            result = await session.execute(
                select(CourseEntryTestResult)
                .options(
                    selectinload(CourseEntryTestResult.student).selectinload(Student.user),
                    selectinload(CourseEntryTestResult.subject),
                    selectinload(CourseEntryTestResult.question_results)
                )
                .where(
                    and_(
                        CourseEntryTestResult.student_id == student_id,
                        CourseEntryTestResult.subject_id == subject_id
                    )
                )
            )
            return result.scalar_one_or_none()

    @staticmethod
    async def has_student_taken_test(student_id: int, subject_id: int) -> bool:
        """Проверить, проходил ли студент входной тест по предмету"""
        result = await CourseEntryTestResultRepository.get_by_student_and_subject(student_id, subject_id)
        return result is not None

    @staticmethod
    async def get_random_questions_for_subject(subject_id: int, count: int = 30) -> List[Question]:
        """Получить случайные вопросы из всех ДЗ предмета (из всех курсов)"""
        async with get_db_session() as session:
            # Получаем все вопросы из ДЗ данного предмета
            result = await session.execute(
                select(Question)
                .options(
                    selectinload(Question.answer_options),
                    selectinload(Question.homework).selectinload(Homework.lesson)
                )
                .join(Homework, Question.homework_id == Homework.id)
                .join(Lesson, Homework.lesson_id == Lesson.id)
                .where(Lesson.subject_id == subject_id)
                .order_by(func.random())  # Случайный порядок
                .limit(count)
            )
            return list(result.scalars().all())

    @staticmethod
    async def create_test_result(student_id: int, subject_id: int, 
                               question_results: List[Dict]) -> CourseEntryTestResult:
        """Создать результат входного теста курса"""
        async with get_db_session() as session:
            # Подсчитываем правильные ответы
            correct_answers = sum(1 for qr in question_results if qr['is_correct'])
            total_questions = len(question_results)
            score_percentage = int((correct_answers / total_questions) * 100) if total_questions > 0 else 0
            
            # Создаем основной результат
            test_result = CourseEntryTestResult(
                student_id=student_id,
                subject_id=subject_id,
                total_questions=total_questions,
                correct_answers=correct_answers,
                score_percentage=score_percentage
            )
            session.add(test_result)
            await session.flush()  # Получаем ID
            
            # Создаем результаты ответов на вопросы
            for qr_data in question_results:
                question_result = CourseEntryQuestionResult(
                    test_result_id=test_result.id,
                    question_id=qr_data['question_id'],
                    selected_answer_id=qr_data.get('selected_answer_id'),
                    is_correct=qr_data['is_correct'],
                    time_spent=qr_data.get('time_spent'),
                    microtopic_number=qr_data.get('microtopic_number')
                )
                session.add(question_result)
            
            await session.commit()

            # Загружаем объект с связанными данными
            result = await session.execute(
                select(CourseEntryTestResult)
                .options(
                    selectinload(CourseEntryTestResult.student).selectinload(Student.user),
                    selectinload(CourseEntryTestResult.subject),
                    selectinload(CourseEntryTestResult.question_results)
                )
                .where(CourseEntryTestResult.id == test_result.id)
            )
            return result.scalar_one()

    @staticmethod
    async def get_statistics_by_group(group_id: int) -> Dict:
        """Получить статистику входного теста курса по группе"""
        async with get_db_session() as session:
            from ..models import student_groups
            
            # Получаем группу с предметом
            group_result = await session.execute(
                select(Group)
                .options(selectinload(Group.subject))
                .where(Group.id == group_id)
            )
            group = group_result.scalar_one_or_none()
            
            if not group:
                return {"completed": [], "not_completed": [], "group_name": "Неизвестная группа"}
            
            # Получаем всех студентов группы
            students_result = await session.execute(
                select(Student)
                .options(selectinload(Student.user))
                .join(student_groups, Student.id == student_groups.c.student_id)
                .where(student_groups.c.group_id == group_id)
            )
            all_students = list(students_result.scalars().all())
            
            # Получаем результаты тестов для студентов группы по предмету группы
            test_results = await session.execute(
                select(CourseEntryTestResult)
                .options(
                    selectinload(CourseEntryTestResult.student).selectinload(Student.user),
                    selectinload(CourseEntryTestResult.question_results)
                )
                .join(Student, CourseEntryTestResult.student_id == Student.id)
                .join(student_groups, Student.id == student_groups.c.student_id)
                .where(
                    and_(
                        student_groups.c.group_id == group_id,
                        CourseEntryTestResult.subject_id == group.subject_id
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
                "test_results": completed_results
            }

    @staticmethod
    async def get_microtopic_statistics(test_result_id: int) -> Dict[int, Dict]:
        """Получить статистику по микротемам для результата теста"""
        async with get_db_session() as session:
            # Получаем результаты ответов с микротемами
            result = await session.execute(
                select(CourseEntryQuestionResult)
                .where(CourseEntryQuestionResult.test_result_id == test_result_id)
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
    async def delete(test_result_id: int) -> bool:
        """Удалить результат теста"""
        async with get_db_session() as session:
            result = await session.execute(
                delete(CourseEntryTestResult).where(CourseEntryTestResult.id == test_result_id)
            )
            await session.commit()
            return result.rowcount > 0
