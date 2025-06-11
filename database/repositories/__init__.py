"""
Репозитории для работы с базой данных
"""
from .user_repository import UserRepository
from .course_repository import CourseRepository
from .subject_repository import SubjectRepository
from .group_repository import GroupRepository
from .student_repository import StudentRepository
from .curator_repository import CuratorRepository
from .teacher_repository import TeacherRepository
from .manager_repository import ManagerRepository

__all__ = [
    'UserRepository',
    'CourseRepository',
    'SubjectRepository',
    'GroupRepository',
    'StudentRepository',
    'CuratorRepository',
    'TeacherRepository',
    'ManagerRepository'
]
