"""
Репозиторий для работы с домашними заданиями
"""
from typing import List, Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from ..models import Homework, User, Course, Subject, Lesson
from ..database import get_db_session


class HomeworkRepository:
    """Репозиторий для работы с домашними заданиями"""
    
    @staticmethod
    async def get_all() -> List[Homework]:
        """Получить все домашние задания"""
        async with get_db_session() as session:
            result = await session.execute(
                select(Homework)
                .options(
                    selectinload(Homework.course),
                    selectinload(Homework.subject),
                    selectinload(Homework.lesson),
                    selectinload(Homework.creator),
                    selectinload(Homework.questions)
                )
            )
            return list(result.scalars().all())

    @staticmethod
    async def get_by_id(homework_id: int) -> Optional[Homework]:
        """Получить домашнее задание по ID"""
        async with get_db_session() as session:
            result = await session.execute(
                select(Homework)
                .options(
                    selectinload(Homework.course),
                    selectinload(Homework.subject),
                    selectinload(Homework.lesson),
                    selectinload(Homework.creator),
                    selectinload(Homework.questions)
                )
                .where(Homework.id == homework_id)
            )
            return result.scalar_one_or_none()

    @staticmethod
    async def get_by_lesson(lesson_id: int) -> List[Homework]:
        """Получить все домашние задания по уроку"""
        async with get_db_session() as session:
            result = await session.execute(
                select(Homework)
                .options(
                    selectinload(Homework.course),
                    selectinload(Homework.subject),
                    selectinload(Homework.lesson),
                    selectinload(Homework.creator)
                )
                .where(Homework.lesson_id == lesson_id)
                .order_by(Homework.created_at.desc())
            )
            return list(result.scalars().all())

    @staticmethod
    async def get_by_course_subject_lesson(course_id: int, subject_id: int, lesson_id: int) -> List[Homework]:
        """Получить домашние задания по курсу, предмету и уроку"""
        async with get_db_session() as session:
            result = await session.execute(
                select(Homework)
                .options(
                    selectinload(Homework.course),
                    selectinload(Homework.subject),
                    selectinload(Homework.lesson),
                    selectinload(Homework.creator)
                )
                .where(
                    Homework.course_id == course_id,
                    Homework.subject_id == subject_id,
                    Homework.lesson_id == lesson_id
                )
                .order_by(Homework.created_at.desc())
            )
            return list(result.scalars().all())

    @staticmethod
    async def get_by_manager(manager_user_id: int) -> List[Homework]:
        """Получить все домашние задания, созданные менеджером"""
        async with get_db_session() as session:
            result = await session.execute(
                select(Homework)
                .options(
                    selectinload(Homework.course),
                    selectinload(Homework.subject),
                    selectinload(Homework.lesson),
                    selectinload(Homework.creator)
                )
                .where(Homework.created_by == manager_user_id)
                .order_by(Homework.created_at.desc())
            )
            return list(result.scalars().all())

    @staticmethod
    async def create(name: str, course_id: int, subject_id: int, lesson_id: int, created_by: int) -> Homework:
        """Создать новое домашнее задание"""
        async with get_db_session() as session:
            # Проверяем уникальность названия в рамках урока
            existing = await session.execute(
                select(Homework).where(
                    Homework.name == name,
                    Homework.lesson_id == lesson_id
                )
            )
            if existing.scalar_one_or_none():
                raise ValueError(f"Домашнее задание с названием '{name}' уже существует в этом уроке")

            # Проверяем существование связанных сущностей
            course_exists = await session.execute(select(Course).where(Course.id == course_id))
            if not course_exists.scalar_one_or_none():
                raise ValueError(f"Курс с ID {course_id} не найден")

            subject_exists = await session.execute(select(Subject).where(Subject.id == subject_id))
            if not subject_exists.scalar_one_or_none():
                raise ValueError(f"Предмет с ID {subject_id} не найден")

            lesson_exists = await session.execute(select(Lesson).where(Lesson.id == lesson_id))
            if not lesson_exists.scalar_one_or_none():
                raise ValueError(f"Урок с ID {lesson_id} не найден")

            user_exists = await session.execute(select(User).where(User.id == created_by))
            if not user_exists.scalar_one_or_none():
                raise ValueError(f"Пользователь с ID {created_by} не найден")

            homework = Homework(
                name=name,
                course_id=course_id,
                subject_id=subject_id,
                lesson_id=lesson_id,
                created_by=created_by
            )
            session.add(homework)
            await session.commit()
            await session.refresh(homework)
            return homework

    @staticmethod
    async def update(homework_id: int, **kwargs) -> Optional[Homework]:
        """Обновить домашнее задание"""
        async with get_db_session() as session:
            homework = await session.get(Homework, homework_id)
            if not homework:
                return None

            # Проверяем уникальность названия при изменении
            if 'name' in kwargs:
                existing = await session.execute(
                    select(Homework).where(
                        Homework.name == kwargs['name'],
                        Homework.lesson_id == homework.lesson_id,
                        Homework.id != homework_id
                    )
                )
                if existing.scalar_one_or_none():
                    raise ValueError(f"Домашнее задание с названием '{kwargs['name']}' уже существует в этом уроке")

            for key, value in kwargs.items():
                if hasattr(homework, key):
                    setattr(homework, key, value)

            await session.commit()
            await session.refresh(homework)
            return homework

    @staticmethod
    async def delete(homework_id: int) -> bool:
        """Удалить домашнее задание"""
        async with get_db_session() as session:
            result = await session.execute(
                delete(Homework).where(Homework.id == homework_id)
            )
            await session.commit()
            return result.rowcount > 0

    @staticmethod
    async def exists_by_name_and_lesson(name: str, lesson_id: int) -> bool:
        """Проверить существование ДЗ по названию и уроку"""
        async with get_db_session() as session:
            result = await session.execute(
                select(Homework).where(
                    Homework.name == name,
                    Homework.lesson_id == lesson_id
                )
            )
            return result.scalar_one_or_none() is not None
