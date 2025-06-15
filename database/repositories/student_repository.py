"""
Репозиторий для работы со студентами
"""
from typing import List, Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from ..models import Student, User, Group
from ..database import get_db_session


class StudentRepository:
    """Репозиторий для работы со студентами"""
    
    @staticmethod
    async def get_all() -> List[Student]:
        """Получить всех студентов"""
        async with get_db_session() as session:
            result = await session.execute(
                select(Student)
                .options(
                    selectinload(Student.user),
                    selectinload(Student.group).selectinload(Group.subject)
                )

            )
            return list(result.scalars().all())

    @staticmethod
    async def get_by_id(student_id: int) -> Optional[Student]:
        """Получить студента по ID"""
        async with get_db_session() as session:
            result = await session.execute(
                select(Student)
                .options(
                    selectinload(Student.user),
                    selectinload(Student.group).selectinload(Group.subject)
                )
                .where(Student.id == student_id)
            )
            return result.scalar_one_or_none()

    @staticmethod
    async def get_by_user_id(user_id: int) -> Optional[Student]:
        """Получить студента по ID пользователя"""
        async with get_db_session() as session:
            result = await session.execute(
                select(Student)
                .options(
                    selectinload(Student.user),
                    selectinload(Student.group).selectinload(Group.subject)
                )
                .where(Student.user_id == user_id)
            )
            return result.scalar_one_or_none()

    @staticmethod
    async def get_by_group(group_id: int) -> List[Student]:
        """Получить студентов по группе"""
        async with get_db_session() as session:
            result = await session.execute(
                select(Student)
                .options(
                    selectinload(Student.user),
                    selectinload(Student.group).selectinload(Group.subject)
                )
                .where(Student.group_id == group_id)

            )
            return list(result.scalars().all())

    @staticmethod
    async def get_by_course_and_group(course_id: int = None, group_id: int = None) -> List[Student]:
        """Получить студентов по курсу и/или группе"""
        async with get_db_session() as session:
            query = select(Student).options(
                selectinload(Student.user),
                selectinload(Student.group).selectinload(Group.subject)
            )
            
            if group_id:
                query = query.where(Student.group_id == group_id)
            elif course_id:
                # Если указан курс, но не группа, получаем студентов всех групп курса
                from ..models import Subject, course_subjects
                query = query.join(Student.group).join(Group.subject).join(
                    course_subjects, Subject.id == course_subjects.c.subject_id
                ).where(course_subjects.c.course_id == course_id)
                
            result = await session.execute(query)
            return list(result.scalars().all())

    @staticmethod
    async def create(user_id: int, group_id: int = None, tariff: str = None) -> Student:
        """Создать профиль студента"""
        async with get_db_session() as session:
            # Проверяем, существует ли уже профиль студента для этого пользователя
            existing = await session.execute(
                select(Student).where(Student.user_id == user_id)
            )
            if existing.scalar_one_or_none():
                raise ValueError(f"Профиль студента для пользователя {user_id} уже существует")

            # Проверяем, существует ли пользователь
            user_exists = await session.execute(
                select(User).where(User.id == user_id)
            )
            if not user_exists.scalar_one_or_none():
                raise ValueError(f"Пользователь с ID {user_id} не найден")

            student = Student(
                user_id=user_id,
                group_id=group_id,
                tariff=tariff
            )
            session.add(student)
            await session.commit()
            await session.refresh(student)
            return student

    @staticmethod
    async def update(student_id: int, group_id: int = None, tariff: str = None, 
                    points: int = None, level: str = None) -> bool:
        """Обновить информацию о студенте"""
        async with get_db_session() as session:
            student = await session.get(Student, student_id)
            if not student:
                return False
            
            if group_id is not None:
                student.group_id = group_id
            if tariff is not None:
                student.tariff = tariff
            if points is not None:
                student.points = points
            if level is not None:
                student.level = level
                
            await session.commit()
            return True

    @staticmethod
    async def delete(student_id: int) -> bool:
        """Удалить профиль студента"""
        async with get_db_session() as session:
            result = await session.execute(delete(Student).where(Student.id == student_id))
            await session.commit()
            return result.rowcount > 0

    @staticmethod
    async def delete_by_user_id(user_id: int) -> bool:
        """Удалить профиль студента по ID пользователя"""
        async with get_db_session() as session:
            result = await session.execute(delete(Student).where(Student.user_id == user_id))
            await session.commit()
            return result.rowcount > 0

    @staticmethod
    async def get_general_stats(student_id: int) -> dict:
        """Получить общую статистику студента"""
        from .homework_result_repository import HomeworkResultRepository
        return await HomeworkResultRepository.get_student_stats(student_id)

    @staticmethod
    async def get_microtopic_understanding(student_id: int, subject_id: int) -> dict:
        """Получить понимание по микротемам для предмета"""
        from .homework_result_repository import HomeworkResultRepository
        return await HomeworkResultRepository.get_microtopic_understanding(student_id, subject_id)

    @staticmethod
    async def update_points_and_level(student_id: int) -> bool:
        """Обновить баллы и уровень студента на основе результатов ДЗ"""
        async with get_db_session() as session:
            student = await session.get(Student, student_id)
            if not student:
                return False

            # Получаем общую статистику
            stats = await StudentRepository.get_general_stats(student_id)
            total_points = stats.get('total_points', 0)

            # Определяем уровень на основе баллов
            if total_points >= 1000:
                level = "🏆 Эксперт"
            elif total_points >= 500:
                level = "🧪 Практик"
            elif total_points >= 200:
                level = "📚 Ученик"
            elif total_points >= 50:
                level = "🌱 Начинающий"
            else:
                level = "🆕 Новичок"

            # Обновляем данные студента
            student.points = total_points
            student.level = level

            await session.commit()
            return True
