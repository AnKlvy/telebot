"""
Репозиторий для работы с предметами
"""
from typing import List, Optional
from sqlalchemy import select, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from ..models import Subject, course_subjects
from ..database import get_db_session


class SubjectRepository:
    """Репозиторий для работы с предметами"""
    
    @staticmethod
    async def get_all() -> List[Subject]:
        """Получить все предметы"""
        async with get_db_session() as session:
            result = await session.execute(
                select(Subject)
                .options(selectinload(Subject.courses))
                .order_by(Subject.name)
            )
            return list(result.scalars().all())

    @staticmethod
    async def get_by_id(subject_id: int) -> Optional[Subject]:
        """Получить предмет по ID"""
        async with get_db_session() as session:
            result = await session.execute(
                select(Subject)
                .options(selectinload(Subject.courses))
                .where(Subject.id == subject_id)
            )
            return result.scalar_one_or_none()

    @staticmethod
    async def get_by_name(name: str) -> Optional[Subject]:
        """Получить предмет по названию"""
        async with get_db_session() as session:
            result = await session.execute(
                select(Subject)
                .options(selectinload(Subject.courses))
                .where(Subject.name == name)
            )
            return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_course(course_id: int) -> List[Subject]:
        """Получить предметы по курсу"""
        from ..models import Course
        async with get_db_session() as session:
            result = await session.execute(
                select(Course)
                .options(selectinload(Course.subjects))
                .where(Course.id == course_id)
            )
            course = result.scalar_one_or_none()
            return list(course.subjects) if course else []

    @staticmethod
    async def create(name: str) -> Subject:
        """Создать новый предмет"""
        async with get_db_session() as session:
            # Проверяем, существует ли уже такой предмет
            existing = await session.execute(select(Subject).where(Subject.name == name))
            if existing.scalar_one_or_none():
                raise ValueError(f"Предмет '{name}' уже существует")

            subject = Subject(name=name)
            session.add(subject)
            await session.commit()
            await session.refresh(subject)
            return subject

    @staticmethod
    async def add_to_course(subject_id: int, course_id: int) -> bool:
        """Добавить предмет к курсу"""
        from ..models import Course, course_subjects
        from sqlalchemy import insert, select

        async with get_db_session() as session:
            # Проверяем, существует ли уже такая связь
            existing = await session.execute(
                select(course_subjects).where(
                    course_subjects.c.course_id == course_id,
                    course_subjects.c.subject_id == subject_id
                )
            )

            if existing.first():
                return False  # Связь уже существует

            # Добавляем связь
            await session.execute(
                insert(course_subjects).values(
                    course_id=course_id,
                    subject_id=subject_id
                )
            )
            await session.commit()
            return True
    
    @staticmethod
    async def delete(subject_id: int) -> bool:
        """Удалить предмет, все его связи с курсами и группы"""
        from ..models import course_subjects, TrialEntResult, TrialEntQuestionResult, Question
        from .group_repository import GroupRepository

        # Сначала удаляем все группы предмета (со всеми их связями)
        await GroupRepository.delete_by_subject(subject_id)

        async with get_db_session() as session:
            # Получаем все вопросы предмета, которые будут удалены
            questions_result = await session.execute(
                select(Question.id).where(Question.subject_id == subject_id)
            )
            question_ids = [row[0] for row in questions_result.fetchall()]

            if question_ids:
                # Находим все результаты пробного ЕНТ, которые содержат эти вопросы
                trial_ent_results = await session.execute(
                    select(TrialEntResult.id).distinct()
                    .join(TrialEntQuestionResult, TrialEntResult.id == TrialEntQuestionResult.test_result_id)
                    .where(TrialEntQuestionResult.question_id.in_(question_ids))
                )
                trial_ent_result_ids = [row[0] for row in trial_ent_results.fetchall()]

                if trial_ent_result_ids:
                    # Удаляем результаты ответов на вопросы пробного ЕНТ
                    await session.execute(
                        delete(TrialEntQuestionResult).where(
                            TrialEntQuestionResult.test_result_id.in_(trial_ent_result_ids)
                        )
                    )

                    # Удаляем основные результаты пробного ЕНТ
                    await session.execute(
                        delete(TrialEntResult).where(TrialEntResult.id.in_(trial_ent_result_ids))
                    )

                    print(f"🗑️ Удалено {len(trial_ent_result_ids)} результатов пробного ЕНТ, содержащих вопросы удаляемого предмета")

            # Затем удаляем связи с курсами
            await session.execute(
                delete(course_subjects).where(course_subjects.c.subject_id == subject_id)
            )

            # Наконец удаляем сам предмет
            result = await session.execute(delete(Subject).where(Subject.id == subject_id))
            await session.commit()
            return result.rowcount > 0

    @staticmethod
    async def get_by_student(student_id: int) -> List[Subject]:
        """Получить уникальные предметы студента из всех его курсов"""
        async with get_db_session() as session:
            from ..models import Course, course_subjects, student_courses
            result = await session.execute(
                select(Subject)
                .options(selectinload(Subject.courses))
                .join(course_subjects, Subject.id == course_subjects.c.subject_id)
                .join(Course, Course.id == course_subjects.c.course_id)
                .join(student_courses, Course.id == student_courses.c.course_id)
                .where(student_courses.c.student_id == student_id)
                .distinct()
                .order_by(Subject.name)
            )
            return list(result.scalars().all())

    @staticmethod
    async def get_by_user_id(telegram_id: int) -> List[Subject]:
        """Получить уникальные предметы студента по telegram_id"""
        async with get_db_session() as session:
            from ..models import Course, course_subjects, student_courses, Student, User
            result = await session.execute(
                select(Subject)
                .options(selectinload(Subject.courses))
                .join(course_subjects, Subject.id == course_subjects.c.subject_id)
                .join(Course, Course.id == course_subjects.c.course_id)
                .join(student_courses, Course.id == student_courses.c.course_id)
                .join(Student, Student.id == student_courses.c.student_id)
                .join(User, Student.user_id == User.id)
                .where(User.telegram_id == telegram_id)
                .distinct()
                .order_by(Subject.name)
            )
            return list(result.scalars().all())
