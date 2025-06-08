"""
Репозитории для работы с базой данных
"""
from .user_repository import UserRepository
from .course_repository import CourseRepository
from .subject_repository import SubjectRepository

__all__ = [
    'UserRepository',
    'CourseRepository',
    'SubjectRepository'
]
