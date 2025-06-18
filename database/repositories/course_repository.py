"""
Репозиторий для работы с курсами
"""
from typing import List, Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from ..models import Course, course_subjects
from ..database import get_db_session


class CourseRepository:
    """Репозиторий для работы с курсами"""
    
    @staticmethod
    async def get_all() -> List[Course]:
        """Получить все курсы"""
        async with get_db_session() as session:
            result = await session.execute(
                select(Course)
                .options(selectinload(Course.subjects))
                .order_by(Course.name)
            )
            return list(result.scalars().all())
    
    @staticmethod
    async def get_by_id(course_id: int) -> Optional[Course]:
        """Получить курс по ID"""
        async with get_db_session() as session:
            result = await session.execute(
                select(Course)
                .options(selectinload(Course.subjects))
                .where(Course.id == course_id)
            )
            return result.scalar_one_or_none()
    
    @staticmethod
    async def create(name: str) -> Course:
        """Создать новый курс"""
        async with get_db_session() as session:
            course = Course(name=name)
            session.add(course)
            await session.commit()
            await session.refresh(course)
            return course
    
    @staticmethod
    async def delete(course_id: int) -> bool:
        """Удалить курс и все его связи с предметами"""
        from ..models import course_subjects
        async with get_db_session() as session:
            # Сначала удаляем связи с предметами
            await session.execute(
                delete(course_subjects).where(course_subjects.c.course_id == course_id)
            )

            # Затем удаляем сам курс
            result = await session.execute(delete(Course).where(Course.id == course_id))
            await session.commit()
            return result.rowcount > 0

    @staticmethod
    async def get_by_student(student_id: int) -> List[Course]:
        """Получить курсы студента"""
        async with get_db_session() as session:
            from ..models import Student, student_courses
            result = await session.execute(
                select(Course)
                .options(selectinload(Course.subjects))
                .join(student_courses, Course.id == student_courses.c.course_id)
                .where(student_courses.c.student_id == student_id)
                .order_by(Course.name)
            )
            return list(result.scalars().all())

    @staticmethod
    async def get_by_user_id(user_id: int) -> List[Course]:
        """Получить курсы студента по user_id"""
        async with get_db_session() as session:
            from ..models import Student, student_courses
            result = await session.execute(
                select(Course)
                .options(selectinload(Course.subjects))
                .join(student_courses, Course.id == student_courses.c.course_id)
                .join(Student, Student.id == student_courses.c.student_id)
                .where(Student.user_id == user_id)
                .order_by(Course.name)
            )
            return list(result.scalars().all())
