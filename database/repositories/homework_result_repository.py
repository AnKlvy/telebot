"""
Репозиторий для работы с результатами домашних заданий
"""
from sqlalchemy import select, func, and_, case
from sqlalchemy.orm import selectinload
from ..database import get_db_session
from ..models import HomeworkResult, QuestionResult, Student, Homework, Question


class HomeworkResultRepository:
    """Репозиторий для работы с результатами домашних заданий"""

    @staticmethod
    async def create(student_id: int, homework_id: int, total_questions: int,
                    correct_answers: int, points_earned: int, is_first_attempt: bool = True,
                    points_awarded: bool = False) -> HomeworkResult:
        """Создать результат домашнего задания"""
        async with get_db_session() as session:
            homework_result = HomeworkResult(
                student_id=student_id,
                homework_id=homework_id,
                total_questions=total_questions,
                correct_answers=correct_answers,
                points_earned=points_earned,
                is_first_attempt=is_first_attempt,
                points_awarded=points_awarded
            )
            session.add(homework_result)
            await session.commit()
            await session.refresh(homework_result)
            return homework_result

    @staticmethod
    async def get_by_id(homework_result_id: int) -> HomeworkResult:
        """Получить результат по ID"""
        async with get_db_session() as session:
            result = await session.execute(
                select(HomeworkResult)
                .options(selectinload(HomeworkResult.question_results))
                .where(HomeworkResult.id == homework_result_id)
            )
            return result.scalar_one_or_none()

    @staticmethod
    async def get_by_student(student_id: int) -> list[HomeworkResult]:
        """Получить все результаты студента"""
        async with get_db_session() as session:
            result = await session.execute(
                select(HomeworkResult)
                .options(
                    selectinload(HomeworkResult.homework).selectinload(Homework.subject)
                )
                .where(HomeworkResult.student_id == student_id)
                .order_by(HomeworkResult.completed_at.desc())
            )
            return result.scalars().all()

    @staticmethod
    async def get_by_homework(homework_id: int) -> list[HomeworkResult]:
        """Получить все результаты по домашнему заданию"""
        async with get_db_session() as session:
            result = await session.execute(
                select(HomeworkResult)
                .options(selectinload(HomeworkResult.student))
                .where(HomeworkResult.homework_id == homework_id)
                .order_by(HomeworkResult.completed_at.desc())
            )
            return result.scalars().all()

    @staticmethod
    async def get_student_homework_attempts(student_id: int, homework_id: int) -> list[HomeworkResult]:
        """Получить все попытки студента по конкретному ДЗ"""
        async with get_db_session() as session:
            result = await session.execute(
                select(HomeworkResult)
                .where(and_(
                    HomeworkResult.student_id == student_id,
                    HomeworkResult.homework_id == homework_id
                ))
                .order_by(HomeworkResult.completed_at.asc())
            )
            return result.scalars().all()

    @staticmethod
    async def has_perfect_score(student_id: int, homework_id: int) -> bool:
        """Проверить, есть ли у студента 100% результат по ДЗ"""
        async with get_db_session() as session:
            result = await session.execute(
                select(func.count(HomeworkResult.id))
                .where(and_(
                    HomeworkResult.student_id == student_id,
                    HomeworkResult.homework_id == homework_id,
                    HomeworkResult.correct_answers == HomeworkResult.total_questions
                ))
            )
            count = result.scalar() or 0
            return count > 0

    @staticmethod
    async def has_points_awarded(student_id: int, homework_id: int) -> bool:
        """Проверить, были ли уже начислены баллы за это ДЗ"""
        async with get_db_session() as session:
            result = await session.execute(
                select(func.count(HomeworkResult.id))
                .where(and_(
                    HomeworkResult.student_id == student_id,
                    HomeworkResult.homework_id == homework_id,
                    HomeworkResult.points_awarded == True
                ))
            )
            count = result.scalar() or 0
            return count > 0

    @staticmethod
    async def get_student_stats(student_id: int) -> dict:
        """Получить общую статистику студента"""
        async with get_db_session() as session:
            # Получаем студента и его группы
            from ..models import Student, Homework, Group
            student_result = await session.execute(
                select(Student)
                .options(selectinload(Student.groups))
                .where(Student.id == student_id)
            )
            student = student_result.scalar_one_or_none()

            if not student or not student.groups:
                # Если нет групп, считаем общие баллы без привязки к предмету
                total_points_result = await session.execute(
                    select(func.sum(HomeworkResult.points_earned))
                    .where(HomeworkResult.student_id == student_id)
                )
                total_points = total_points_result.scalar() or 0

                return {
                    'total_completed': 0,
                    'total_available': 0,
                    'unique_completed': 0,
                    'total_points': total_points
                }

            # Получаем все предметы из групп студента
            subject_ids = [group.subject_id for group in student.groups if group.subject_id]

            if not subject_ids:
                # Если нет предметов, считаем только общие баллы
                total_points_result = await session.execute(
                    select(func.sum(HomeworkResult.points_earned))
                    .where(HomeworkResult.student_id == student_id)
                )
                total_points = total_points_result.scalar() or 0

                return {
                    'total_completed': 0,
                    'total_available': 0,
                    'unique_completed': 0,
                    'total_points': total_points
                }

            # Общее количество доступных ДЗ для всех предметов групп студента
            total_available_result = await session.execute(
                select(func.count(Homework.id))
                .where(Homework.subject_id.in_(subject_ids))
            )
            total_available = total_available_result.scalar() or 0

            # Количество уникальных выполненных ДЗ по всем предметам групп студента (без повторов)
            unique_completed_result = await session.execute(
                select(func.count(func.distinct(HomeworkResult.homework_id)))
                .join(Homework, HomeworkResult.homework_id == Homework.id)
                .where(
                    HomeworkResult.student_id == student_id,
                    Homework.subject_id.in_(subject_ids)
                )
            )
            unique_completed = unique_completed_result.scalar() or 0

            # Общее количество выполненных ДЗ по всем предметам групп (включая повторные)
            total_completed_result = await session.execute(
                select(func.count(HomeworkResult.id))
                .join(Homework, HomeworkResult.homework_id == Homework.id)
                .where(
                    HomeworkResult.student_id == student_id,
                    Homework.subject_id.in_(subject_ids)
                )
            )
            total_completed = total_completed_result.scalar() or 0

            # Общие баллы (все баллы студента, не только по предметам групп)
            total_points_result = await session.execute(
                select(func.sum(HomeworkResult.points_earned))
                .where(HomeworkResult.student_id == student_id)
            )
            total_points = total_points_result.scalar() or 0

            return {
                'total_completed': total_completed,
                'total_available': total_available,  # Всего доступных ДЗ
                'unique_completed': unique_completed,  # Уникальных выполненных
                'total_points': total_points
            }

    @staticmethod
    async def get_microtopic_understanding(student_id: int, subject_id: int) -> dict:
        """Получить понимание по микротемам для предмета"""
        async with get_db_session() as session:
            # Получаем статистику по микротемам через результаты вопросов
            result = await session.execute(
                select(
                    QuestionResult.microtopic_number,
                    func.count(QuestionResult.id).label('total_answered'),
                    func.sum(
                        case(
                            (QuestionResult.is_correct == True, 1),
                            else_=0
                        )
                    ).label('correct_answered')
                )
                .join(HomeworkResult, QuestionResult.homework_result_id == HomeworkResult.id)
                .join(Question, QuestionResult.question_id == Question.id)
                .where(and_(
                    HomeworkResult.student_id == student_id,
                    Question.subject_id == subject_id,
                    ~QuestionResult.microtopic_number.is_(None)
                ))
                .group_by(QuestionResult.microtopic_number)
            )

            microtopic_stats = {}
            for row in result:
                microtopic_number = row.microtopic_number
                total = row.total_answered
                correct = row.correct_answered or 0
                percentage = round((correct / total * 100), 0) if total > 0 else 0

                microtopic_stats[microtopic_number] = {
                    'total_answered': total,
                    'correct_answered': correct,
                    'percentage': percentage
                }

            return microtopic_stats

    @staticmethod
    async def delete(homework_result_id: int) -> bool:
        """Удалить результат домашнего задания"""
        async with get_db_session() as session:
            result = await session.execute(
                select(HomeworkResult).where(HomeworkResult.id == homework_result_id)
            )
            homework_result = result.scalar_one_or_none()
            
            if homework_result:
                await session.delete(homework_result)
                await session.commit()
                return True
            return False

    @staticmethod
    async def get_all() -> list[HomeworkResult]:
        """Получить все результаты"""
        async with get_db_session() as session:
            result = await session.execute(
                select(HomeworkResult)
                .options(
                    selectinload(HomeworkResult.student),
                    selectinload(HomeworkResult.homework)
                )
                .order_by(HomeworkResult.completed_at.desc())
            )
            return result.scalars().all()
