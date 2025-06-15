"""
Модели SQLAlchemy для базы данных
"""
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy import Column, Integer, BigInteger, String, Text, DateTime, ForeignKey, Table, UniqueConstraint, Boolean
from sqlalchemy.sql import func


# Базовый класс для моделей
class Base(DeclarativeBase):
    pass


# Таблица связи Many-to-Many для курсов и предметов
course_subjects = Table(
    'course_subjects',
    Base.metadata,
    Column('course_id', Integer, ForeignKey('courses.id'), primary_key=True),
    Column('subject_id', Integer, ForeignKey('subjects.id'), primary_key=True)
)


# Модель пользователя
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    role = Column(String(50), default='student')
    created_at = Column(DateTime, server_default=func.now())


# Модель курса
class Course(Base):
    __tablename__ = 'courses'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    # Связь Many-to-Many с предметами
    subjects = relationship("Subject", secondary=course_subjects, back_populates="courses")


# Модель предмета
class Subject(Base):
    __tablename__ = 'subjects'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)  # Уникальное имя предмета
    created_at = Column(DateTime, server_default=func.now())

    # Связь Many-to-Many с курсами
    courses = relationship("Course", secondary=course_subjects, back_populates="subjects")
    # Связь One-to-Many с группами
    groups = relationship("Group", back_populates="subject", cascade="all, delete-orphan")


# Модель группы
class Group(Base):
    __tablename__ = 'groups'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    subject_id = Column(Integer, ForeignKey('subjects.id'), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    # Связь Many-to-One с предметом
    subject = relationship("Subject", back_populates="groups")


# Модель студента
class Student(Base):
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    group_id = Column(Integer, ForeignKey('groups.id', ondelete='SET NULL'), nullable=True)
    tariff = Column(String(50), nullable=True)  # 'standard' или 'premium'
    points = Column(Integer, default=0)
    level = Column(String(50), default='Новичок')
    created_at = Column(DateTime, server_default=func.now())

    # Связи
    user = relationship("User", backref="student_profile")
    group = relationship("Group", backref="students")


# Модель куратора
class Curator(Base):
    __tablename__ = 'curators'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    course_id = Column(Integer, ForeignKey('courses.id', ondelete='SET NULL'), nullable=True)
    subject_id = Column(Integer, ForeignKey('subjects.id', ondelete='SET NULL'), nullable=True)
    group_id = Column(Integer, ForeignKey('groups.id', ondelete='SET NULL'), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    # Связи
    user = relationship("User", backref="curator_profile")
    course = relationship("Course", backref="curators")
    subject = relationship("Subject", backref="curators")
    group = relationship("Group", backref="curator")


# Модель преподавателя
class Teacher(Base):
    __tablename__ = 'teachers'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    course_id = Column(Integer, ForeignKey('courses.id', ondelete='SET NULL'), nullable=True)
    subject_id = Column(Integer, ForeignKey('subjects.id', ondelete='SET NULL'), nullable=True)
    group_id = Column(Integer, ForeignKey('groups.id', ondelete='SET NULL'), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    # Связи
    user = relationship("User", backref="teacher_profile")
    course = relationship("Course", backref="teachers")
    subject = relationship("Subject", backref="teachers")
    group = relationship("Group", backref="teacher")


# Модель менеджера
class Manager(Base):
    __tablename__ = 'managers'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    created_at = Column(DateTime, server_default=func.now())

    # Связи
    user = relationship("User", backref="manager_profile")


# Модель урока
class Lesson(Base):
    __tablename__ = 'lessons'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    subject_id = Column(Integer, ForeignKey('subjects.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    # Связи
    subject = relationship("Subject", backref="lessons")

    # Уникальность: одно название урока на предмет
    __table_args__ = (
        UniqueConstraint('name', 'subject_id', name='unique_lesson_per_subject'),
    )


# Модель микротемы
class Microtopic(Base):
    __tablename__ = 'microtopics'

    id = Column(Integer, primary_key=True)
    number = Column(Integer, nullable=False)  # Номер микротемы в рамках предмета (1, 2, 3...)
    name = Column(String(255), nullable=False)
    subject_id = Column(Integer, ForeignKey('subjects.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    # Связи
    subject = relationship("Subject", backref="microtopics")

    # Уникальность: один номер микротемы на предмет
    __table_args__ = (
        UniqueConstraint('number', 'subject_id', name='unique_microtopic_number_per_subject'),
    )


# Модель домашнего задания
class Homework(Base):
    __tablename__ = 'homeworks'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    subject_id = Column(Integer, ForeignKey('subjects.id', ondelete='CASCADE'), nullable=False)
    lesson_id = Column(Integer, ForeignKey('lessons.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    # Связи
    subject = relationship("Subject", backref="homeworks")
    lesson = relationship("Lesson", backref="homeworks")
    questions = relationship("Question", back_populates="homework", cascade="all, delete-orphan")

    # Уникальность: одно название ДЗ на урок
    __table_args__ = (
        UniqueConstraint('name', 'lesson_id', name='unique_homework_per_lesson'),
    )


# Модель вопроса
class Question(Base):
    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True)
    homework_id = Column(Integer, ForeignKey('homeworks.id', ondelete='CASCADE'), nullable=False)
    text = Column(Text, nullable=False)
    photo_path = Column(String(500), nullable=True)  # file_id фото от Telegram или путь к файлу
    subject_id = Column(Integer, ForeignKey('subjects.id', ondelete='CASCADE'), nullable=False)
    microtopic_number = Column(Integer, nullable=True)  # Номер микротемы в рамках предмета
    time_limit = Column(Integer, nullable=False, default=30)  # Время в секундах
    order_number = Column(Integer, nullable=False, default=1)  # Порядок вопроса в ДЗ
    created_at = Column(DateTime, server_default=func.now())

    # Связи
    homework = relationship("Homework", back_populates="questions")
    subject = relationship("Subject", backref="questions")
    answer_options = relationship("AnswerOption", back_populates="question", cascade="all, delete-orphan")

    async def get_microtopic(self):
        """Асинхронное получение микротемы по subject_id и microtopic_number"""
        if self.subject_id and self.microtopic_number:
            from database.repositories.microtopic_repository import MicrotopicRepository
            microtopics = await MicrotopicRepository.get_by_subject(self.subject_id)
            for microtopic in microtopics:
                if microtopic.number == self.microtopic_number:
                    return microtopic
        return None

    # Уникальность: один порядковый номер на ДЗ
    __table_args__ = (
        UniqueConstraint('homework_id', 'order_number', name='unique_question_order_per_homework'),
    )


# Модель варианта ответа
class AnswerOption(Base):
    __tablename__ = 'answer_options'

    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey('questions.id', ondelete='CASCADE'), nullable=False)
    text = Column(Text, nullable=False)
    is_correct = Column(Boolean, nullable=False, default=False)
    order_number = Column(Integer, nullable=False, default=1)  # Порядок варианта (A, B, C, D...)
    created_at = Column(DateTime, server_default=func.now())

    # Связи
    question = relationship("Question", back_populates="answer_options")

    # Уникальность: один порядковый номер на вопрос
    __table_args__ = (
        UniqueConstraint('question_id', 'order_number', name='unique_answer_order_per_question'),
    )


# Модель бонусного теста
class BonusTest(Base):
    __tablename__ = 'bonus_tests'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    price = Column(Integer, nullable=False, default=0)  # Цена в монетах
    created_at = Column(DateTime, server_default=func.now())

    # Связи
    questions = relationship("BonusQuestion", back_populates="bonus_test", cascade="all, delete-orphan")


# Модель вопроса бонусного теста
class BonusQuestion(Base):
    __tablename__ = 'bonus_questions'

    id = Column(Integer, primary_key=True)
    bonus_test_id = Column(Integer, ForeignKey('bonus_tests.id', ondelete='CASCADE'), nullable=False)
    text = Column(Text, nullable=False)
    photo_path = Column(String(500), nullable=True)  # file_id фото от Telegram или путь к файлу
    time_limit = Column(Integer, nullable=False, default=30)  # Время в секундах
    order_number = Column(Integer, nullable=False, default=1)  # Порядок вопроса в тесте
    created_at = Column(DateTime, server_default=func.now())

    # Связи
    bonus_test = relationship("BonusTest", back_populates="questions")
    answer_options = relationship("BonusAnswerOption", back_populates="bonus_question", cascade="all, delete-orphan")

    # Уникальность: один порядковый номер на бонусный тест
    __table_args__ = (
        UniqueConstraint('bonus_test_id', 'order_number', name='unique_bonus_question_order_per_test'),
    )


# Модель варианта ответа для бонусного теста
class BonusAnswerOption(Base):
    __tablename__ = 'bonus_answer_options'

    id = Column(Integer, primary_key=True)
    bonus_question_id = Column(Integer, ForeignKey('bonus_questions.id', ondelete='CASCADE'), nullable=False)
    text = Column(Text, nullable=False)
    is_correct = Column(Boolean, nullable=False, default=False)
    order_number = Column(Integer, nullable=False, default=1)  # Порядок варианта (A, B, C, D...)
    created_at = Column(DateTime, server_default=func.now())

    # Связи
    bonus_question = relationship("BonusQuestion", back_populates="answer_options")

    # Уникальность: один порядковый номер на бонусный вопрос
    __table_args__ = (
        UniqueConstraint('bonus_question_id', 'order_number', name='unique_bonus_answer_order_per_question'),
    )
