"""
Модуль для работы с базой данных
"""
from .database import init_database, close_database, get_db_session
from .models import User, Course, Subject, Group, Student, Curator, Teacher, Manager, Microtopic, Lesson, Homework, Question, AnswerOption, MonthTest, MonthTestMicrotopic, BonusTest, BonusQuestion, BonusAnswerOption, HomeworkResult, QuestionResult, CourseEntryTestResult, CourseEntryQuestionResult, MonthEntryTestResult, MonthEntryQuestionResult, ShopItem, StudentPurchase, StudentBonusTest
from .repositories import UserRepository, CourseRepository, SubjectRepository, GroupRepository, StudentRepository, \
    CuratorRepository, TeacherRepository, ManagerRepository, MicrotopicRepository, LessonRepository, \
    HomeworkRepository, QuestionRepository, AnswerOptionRepository, MonthTestRepository, \
    MonthTestMicrotopicRepository, BonusTestRepository, BonusQuestionRepository, BonusAnswerOptionRepository, \
    HomeworkResultRepository, QuestionResultRepository, CourseEntryTestResultRepository, MonthEntryTestResultRepository, ShopItemRepository, StudentPurchaseRepository, StudentBonusTestRepository


# Функции для совместимости со старым кодом
async def get_user_role(telegram_id: int) -> str:
    """Получить роль пользователя (функция для совместимости)"""
    return await UserRepository.get_role(telegram_id)

async def get_user_by_telegram_id(telegram_id: int):
    """Получить пользователя по Telegram ID (функция для совместимости)"""
    return await UserRepository.get_by_telegram_id(telegram_id)

async def create_user(telegram_id: int, name: str, role: str = 'student'):
    """Создать пользователя (функция для совместимости)"""
    return await UserRepository.create(telegram_id, name, role)

__all__ = [
    'init_database',
    'close_database',
    'get_db_session',
    'User',
    'Course',
    'Subject',
    'Group',
    'Student',
    'Curator',
    'Teacher',
    'Manager',
    'Microtopic',
    'Lesson',
    'Homework',
    'Question',
    'AnswerOption',
    'MonthTest',
    'MonthTestMicrotopic',
    'BonusTest',
    'BonusQuestion',
    'BonusAnswerOption',
    'HomeworkResult',
    'QuestionResult',
    'CourseEntryTestResult',
    'CourseEntryQuestionResult',
    'MonthEntryTestResult',
    'MonthEntryQuestionResult',
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
    'QuestionResultRepository',
    'CourseEntryTestResultRepository',
    'MonthEntryTestResultRepository',
    'get_user_role',
    'get_user_by_telegram_id',
    'create_user'
]
