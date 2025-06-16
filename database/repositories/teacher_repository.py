"""
Репозиторий для работы с преподавателями
"""
from typing import List, Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from ..models import Teacher, User, Course, Subject, Group
from ..database import get_db_session


class TeacherRepository:
    """Репозиторий для работы с преподавателями"""
    
    @staticmethod
    async def get_all() -> List[Teacher]:
        """Получить всех преподавателей"""
        async with get_db_session() as session:
            result = await session.execute(
                select(Teacher)
                .options(
                    selectinload(Teacher.user),
                    selectinload(Teacher.course),
                    selectinload(Teacher.subject),
                    selectinload(Teacher.groups).selectinload(Group.subject)
                )
            )
            return list(result.scalars().all())

    @staticmethod
    async def get_by_id(teacher_id: int) -> Optional[Teacher]:
        """Получить преподавателя по ID"""
        async with get_db_session() as session:
            result = await session.execute(
                select(Teacher)
                .options(
                    selectinload(Teacher.user),
                    selectinload(Teacher.course),
                    selectinload(Teacher.subject),
                    selectinload(Teacher.group).selectinload(Group.subject)
                )
                .where(Teacher.id == teacher_id)
            )
            return result.scalar_one_or_none()

    @staticmethod
    async def get_by_user_id(user_id: int) -> Optional[Teacher]:
        """Получить преподавателя по ID пользователя"""
        async with get_db_session() as session:
            result = await session.execute(
                select(Teacher)
                .options(
                    selectinload(Teacher.user),
                    selectinload(Teacher.course),
                    selectinload(Teacher.subject),
                    selectinload(Teacher.groups).selectinload(Group.subject)
                )
                .where(Teacher.user_id == user_id)
            )
            return result.scalar_one_or_none()

    @staticmethod
    async def get_by_group(group_id: int) -> List[Teacher]:
        """Получить преподавателей по группе"""
        async with get_db_session() as session:
            result = await session.execute(
                select(Teacher)
                .options(
                    selectinload(Teacher.user),
                    selectinload(Teacher.course),
                    selectinload(Teacher.subject),
                    selectinload(Teacher.groups).selectinload(Group.subject)
                )
                .join(Teacher.groups)
                .where(Group.id == group_id)
            )
            return list(result.scalars().all())

    @staticmethod
    async def get_by_subject_and_group(subject_id: int = None, group_id: int = None) -> List[Teacher]:
        """Получить преподавателей по предмету и/или группе"""
        async with get_db_session() as session:
            query = select(Teacher).options(
                selectinload(Teacher.user),
                selectinload(Teacher.course),
                selectinload(Teacher.subject),
                selectinload(Teacher.groups).selectinload(Group.subject)
            )

            if group_id:
                # Используем join для поиска по группе через M2M связь
                query = query.join(Teacher.groups).where(Group.id == group_id)
            elif subject_id:
                query = query.where(Teacher.subject_id == subject_id)

            result = await session.execute(query)
            return list(result.scalars().all())

    @staticmethod
    async def create(user_id: int, course_id: int = None, subject_id: int = None) -> Teacher:
        """Создать профиль преподавателя"""
        async with get_db_session() as session:
            # Проверяем, существует ли уже профиль преподавателя для этого пользователя
            existing = await session.execute(
                select(Teacher).where(Teacher.user_id == user_id)
            )
            if existing.scalar_one_or_none():
                raise ValueError(f"Профиль преподавателя для пользователя {user_id} уже существует")

            # Проверяем, существует ли пользователь
            user_exists = await session.execute(
                select(User).where(User.id == user_id)
            )
            if not user_exists.scalar_one_or_none():
                raise ValueError(f"Пользователь с ID {user_id} не найден")

            teacher = Teacher(
                user_id=user_id,
                course_id=course_id,
                subject_id=subject_id
            )
            session.add(teacher)
            await session.commit()
            await session.refresh(teacher)
            return teacher

    @staticmethod
    async def update(teacher_id: int, course_id: int = None, subject_id: int = None) -> bool:
        """Обновить информацию о преподавателе"""
        async with get_db_session() as session:
            teacher = await session.get(Teacher, teacher_id)
            if not teacher:
                return False

            if course_id is not None:
                teacher.course_id = course_id
            if subject_id is not None:
                teacher.subject_id = subject_id

            await session.commit()
            return True

    @staticmethod
    async def delete(teacher_id: int) -> bool:
        """Удалить профиль преподавателя"""
        async with get_db_session() as session:
            result = await session.execute(delete(Teacher).where(Teacher.id == teacher_id))
            await session.commit()
            return result.rowcount > 0

    @staticmethod
    async def delete_by_user_id(user_id: int) -> bool:
        """Удалить профиль преподавателя по ID пользователя"""
        async with get_db_session() as session:
            result = await session.execute(delete(Teacher).where(Teacher.user_id == user_id))
            await session.commit()
            return result.rowcount > 0

    @staticmethod
    async def get_teacher_groups(teacher_id: int) -> List[Group]:
        """Получить все группы преподавателя"""
        async with get_db_session() as session:
            # Получаем преподавателя с его группами
            teacher_result = await session.execute(
                select(Teacher)
                .options(selectinload(Teacher.groups).selectinload(Group.subject))
                .where(Teacher.id == teacher_id)
            )
            teacher = teacher_result.scalar_one_or_none()

            if not teacher:
                return []

            # Возвращаем все группы преподавателя
            return list(teacher.groups)

    @staticmethod
    async def add_teacher_to_group(teacher_id: int, group_id: int) -> bool:
        """Добавить преподавателя в группу"""
        async with get_db_session() as session:
            # Получаем преподавателя с загруженными группами
            result = await session.execute(
                select(Teacher)
                .options(selectinload(Teacher.groups))
                .where(Teacher.id == teacher_id)
            )
            teacher = result.scalar_one_or_none()

            # Получаем группу
            group = await session.get(Group, group_id)

            if not teacher or not group:
                return False

            # Добавляем группу к преподавателю, если её там нет
            if group not in teacher.groups:
                teacher.groups.append(group)
                await session.commit()

            return True

    @staticmethod
    async def remove_teacher_from_group(teacher_id: int, group_id: int) -> bool:
        """Удалить преподавателя из группы"""
        async with get_db_session() as session:
            # Получаем преподавателя с загруженными группами
            result = await session.execute(
                select(Teacher)
                .options(selectinload(Teacher.groups))
                .where(Teacher.id == teacher_id)
            )
            teacher = result.scalar_one_or_none()

            # Получаем группу
            group = await session.get(Group, group_id)

            if not teacher or not group:
                return False

            # Удаляем группу у преподавателя, если она там есть
            if group in teacher.groups:
                teacher.groups.remove(group)
                await session.commit()

            return True
