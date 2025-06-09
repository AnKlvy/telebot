"""
Модели SQLAlchemy для базы данных
"""
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy import Column, Integer, BigInteger, String, Text, DateTime, ForeignKey, Table
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
