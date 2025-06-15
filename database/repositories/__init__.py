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
from .microtopic_repository import MicrotopicRepository
from .lesson_repository import LessonRepository
from .homework_repository import HomeworkRepository
from .question_repository import QuestionRepository
from .answer_option_repository import AnswerOptionRepository
from .month_test_repository import MonthTestRepository
from .month_test_microtopic_repository import MonthTestMicrotopicRepository
from .bonus_test_repository import BonusTestRepository
from .bonus_question_repository import BonusQuestionRepository
from .bonus_answer_option_repository import BonusAnswerOptionRepository
from .homework_result_repository import HomeworkResultRepository
from .question_result_repository import QuestionResultRepository

__all__ = [
    'UserRepository',
    'CourseRepository',
    'SubjectRepository',
    'GroupRepository',
    'StudentRepository',
    'CuratorRepository',
    'TeacherRepository',
    'ManagerRepository',
    'MicrotopicRepository',
    'LessonRepository',
    'HomeworkRepository',
    'QuestionRepository',
    'AnswerOptionRepository',
    'MonthTestRepository',
    'MonthTestMicrotopicRepository',
    'BonusTestRepository',
    'BonusQuestionRepository',
    'BonusAnswerOptionRepository',
    'HomeworkResultRepository',
    'QuestionResultRepository'
]
