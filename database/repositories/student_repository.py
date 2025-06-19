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
                    selectinload(Student.groups).selectinload(Group.subject),
                    selectinload(Student.courses)
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
                    selectinload(Student.groups).selectinload(Group.subject),
                    selectinload(Student.courses)
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
                    selectinload(Student.groups).selectinload(Group.subject),
                    selectinload(Student.courses)
                )
                .where(Student.user_id == user_id)
            )
            return result.scalar_one_or_none()

    @staticmethod
    async def get_by_telegram_id(telegram_id: int) -> Optional[Student]:
        """Получить студента по Telegram ID"""
        async with get_db_session() as session:
            from ..models import User
            result = await session.execute(
                select(Student)
                .options(
                    selectinload(Student.user),
                    selectinload(Student.groups).selectinload(Group.subject),
                    selectinload(Student.courses)
                )
                .join(User, Student.user_id == User.id)
                .where(User.telegram_id == telegram_id)
            )
            return result.scalar_one_or_none()

    @staticmethod
    async def get_by_telegram_id(telegram_id: int) -> Optional[Student]:
        """Получить студента по Telegram ID"""
        async with get_db_session() as session:
            result = await session.execute(
                select(Student)
                .options(
                    selectinload(Student.user),
                    selectinload(Student.groups).selectinload(Group.subject),
                    selectinload(Student.courses)
                )
                .join(User, Student.user_id == User.id)
                .where(User.telegram_id == telegram_id)
            )
            return result.scalar_one_or_none()

    @staticmethod
    async def get_by_group(group_id: int) -> List[Student]:
        """Получить студентов по группе"""
        async with get_db_session() as session:
            from ..models import student_groups
            result = await session.execute(
                select(Student)
                .options(
                    selectinload(Student.user),
                    selectinload(Student.groups).selectinload(Group.subject)
                )
                .join(student_groups)
                .where(student_groups.c.group_id == group_id)
            )
            return list(result.scalars().all())

    @staticmethod
    async def get_by_course_and_group(course_id: int = None, group_id: int = None) -> List[Student]:
        """Получить студентов по курсу и/или группе"""
        async with get_db_session() as session:
            query = select(Student).options(
                selectinload(Student.user),
                selectinload(Student.groups).selectinload(Group.subject)
            )

            if group_id:
                # Используем many-to-many связь через student_groups
                from ..models import student_groups
                query = query.join(student_groups).where(student_groups.c.group_id == group_id)
            elif course_id:
                # Если указан курс, но не группа, получаем студентов всех групп курса
                from ..models import Subject, course_subjects, student_groups
                query = query.join(student_groups).join(Group, student_groups.c.group_id == Group.id).join(Group.subject).join(
                    course_subjects, Subject.id == course_subjects.c.subject_id
                ).where(course_subjects.c.course_id == course_id)

            result = await session.execute(query)
            return list(result.scalars().all())

    @staticmethod
    async def create(user_id: int, tariff: str = None) -> Student:
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
                tariff=tariff
            )
            session.add(student)
            await session.commit()
            await session.refresh(student)
            return student

    @staticmethod
    async def add_courses(student_id: int, course_ids: List[int]) -> bool:
        """Добавить курсы студенту"""
        from ..models import Course, student_courses
        async with get_db_session() as session:
            # Проверяем существование студента
            student = await session.get(Student, student_id)
            if not student:
                return False

            # Получаем курсы
            courses_result = await session.execute(
                select(Course).where(Course.id.in_(course_ids))
            )
            courses = list(courses_result.scalars().all())

            if not courses:
                return False

            # Добавляем связи
            for course in courses:
                # Проверяем, нет ли уже такой связи
                existing = await session.execute(
                    select(student_courses).where(
                        student_courses.c.student_id == student_id,
                        student_courses.c.course_id == course.id
                    )
                )
                if not existing.first():
                    await session.execute(
                        student_courses.insert().values(
                            student_id=student_id,
                            course_id=course.id
                        )
                    )

            await session.commit()
            return True

    @staticmethod
    async def set_courses(student_id: int, course_ids: List[int]) -> bool:
        """Установить курсы студенту (заменить все существующие)"""
        from ..models import student_courses
        async with get_db_session() as session:
            # Удаляем все существующие связи
            await session.execute(
                student_courses.delete().where(
                    student_courses.c.student_id == student_id
                )
            )

            # Добавляем новые связи
            if course_ids:
                for course_id in course_ids:
                    await session.execute(
                        student_courses.insert().values(
                            student_id=student_id,
                            course_id=course_id
                        )
                    )

            await session.commit()
            return True

    @staticmethod
    async def add_courses(student_id: int, course_ids: List[int]) -> bool:
        """Добавить курсы студенту"""
        from ..models import Course, student_courses
        async with get_db_session() as session:
            # Проверяем существование студента
            student = await session.get(Student, student_id)
            if not student:
                return False

            # Получаем курсы
            courses_result = await session.execute(
                select(Course).where(Course.id.in_(course_ids))
            )
            courses = list(courses_result.scalars().all())

            if not courses:
                return False

            # Добавляем связи
            for course in courses:
                # Проверяем, нет ли уже такой связи
                existing = await session.execute(
                    select(student_courses).where(
                        student_courses.c.student_id == student_id,
                        student_courses.c.course_id == course.id
                    )
                )
                if not existing.first():
                    await session.execute(
                        student_courses.insert().values(
                            student_id=student_id,
                            course_id=course.id
                        )
                    )

            await session.commit()
            return True

    @staticmethod
    async def remove_courses(student_id: int, course_ids: List[int]) -> bool:
        """Удалить курсы у студента"""
        from ..models import student_courses
        async with get_db_session() as session:
            await session.execute(
                student_courses.delete().where(
                    student_courses.c.student_id == student_id,
                    student_courses.c.course_id.in_(course_ids)
                )
            )
            await session.commit()
            return True

    @staticmethod
    async def set_courses(student_id: int, course_ids: List[int]) -> bool:
        """Установить курсы студенту (заменить все существующие)"""
        from ..models import student_courses
        async with get_db_session() as session:
            # Удаляем все существующие связи
            await session.execute(
                student_courses.delete().where(
                    student_courses.c.student_id == student_id
                )
            )

            # Добавляем новые связи
            if course_ids:
                for course_id in course_ids:
                    await session.execute(
                        student_courses.insert().values(
                            student_id=student_id,
                            course_id=course_id
                        )
                    )

            await session.commit()
            return True

    @staticmethod
    async def add_groups(student_id: int, group_ids: List[int]) -> bool:
        """Добавить группы студенту"""
        from ..models import Group, student_groups
        async with get_db_session() as session:
            # Проверяем существование студента
            student = await session.get(Student, student_id)
            if not student:
                return False

            # Получаем группы
            groups_result = await session.execute(
                select(Group).where(Group.id.in_(group_ids))
            )
            groups = list(groups_result.scalars().all())

            if not groups:
                return False

            # Добавляем связи
            for group in groups:
                # Проверяем, нет ли уже такой связи
                existing = await session.execute(
                    select(student_groups).where(
                        student_groups.c.student_id == student_id,
                        student_groups.c.group_id == group.id
                    )
                )
                if not existing.first():
                    await session.execute(
                        student_groups.insert().values(
                            student_id=student_id,
                            group_id=group.id
                        )
                    )

            await session.commit()
            return True

    @staticmethod
    async def remove_groups(student_id: int, group_ids: List[int]) -> bool:
        """Удалить группы у студента"""
        from ..models import student_groups
        async with get_db_session() as session:
            await session.execute(
                student_groups.delete().where(
                    student_groups.c.student_id == student_id,
                    student_groups.c.group_id.in_(group_ids)
                )
            )
            await session.commit()
            return True

    @staticmethod
    async def set_groups(student_id: int, group_ids: List[int]) -> bool:
        """Установить группы студенту (заменить все существующие)"""
        from ..models import student_groups
        async with get_db_session() as session:
            # Удаляем все существующие связи
            await session.execute(
                student_groups.delete().where(
                    student_groups.c.student_id == student_id
                )
            )

            # Добавляем новые связи
            if group_ids:
                for group_id in group_ids:
                    await session.execute(
                        student_groups.insert().values(
                            student_id=student_id,
                            group_id=group_id
                        )
                    )

            await session.commit()
            return True

    @staticmethod
    async def update(student_id: int, tariff: str = None,
                    points: int = None, level: str = None) -> bool:
        """Обновить информацию о студенте"""
        async with get_db_session() as session:
            student = await session.get(Student, student_id)
            if not student:
                return False

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

    @staticmethod
    async def get_balance(student_id: int) -> dict:
        """Получить баланс студента (баллы и монеты)"""
        async with get_db_session() as session:
            student = await session.get(Student, student_id)
            if not student:
                return {"points": 0, "coins": 0}
            return {"points": student.points, "coins": student.coins}

    @staticmethod
    async def exchange_points_to_coins(student_id: int, points_amount: int) -> bool:
        """Обменять баллы на монеты (1:1)"""
        async with get_db_session() as session:
            student = await session.get(Student, student_id)
            if not student or student.points < points_amount:
                return False

            student.points -= points_amount
            student.coins += points_amount

            await session.commit()
            return True

    @staticmethod
    async def spend_coins(student_id: int, coins_amount: int) -> bool:
        """Потратить монеты"""
        async with get_db_session() as session:
            student = await session.get(Student, student_id)
            if not student or student.coins < coins_amount:
                return False

            student.coins -= coins_amount

            await session.commit()
            return True

    @staticmethod
    async def add_coins(student_id: int, coins_amount: int) -> bool:
        """Добавить монеты студенту"""
        async with get_db_session() as session:
            student = await session.get(Student, student_id)
            if not student:
                return False

            student.coins += coins_amount

            await session.commit()
            return True
