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

# Таблица связи Many-to-Many для кураторов и групп
curator_groups = Table(
    'curator_groups',
    Base.metadata,
    Column('curator_id', Integer, ForeignKey('curators.id'), primary_key=True),
    Column('group_id', Integer, ForeignKey('groups.id'), primary_key=True)
)

# Таблица связи Many-to-Many для учителей и групп
teacher_groups = Table(
    'teacher_groups',
    Base.metadata,
    Column('teacher_id', Integer, ForeignKey('teachers.id'), primary_key=True),
    Column('group_id', Integer, ForeignKey('groups.id'), primary_key=True)
)

# Таблица связи Many-to-Many для студентов и курсов
student_courses = Table(
    'student_courses',
    Base.metadata,
    Column('student_id', Integer, ForeignKey('students.id'), primary_key=True),
    Column('course_id', Integer, ForeignKey('courses.id'), primary_key=True)
)

# Таблица связи Many-to-Many для студентов и групп
student_groups = Table(
    'student_groups',
    Base.metadata,
    Column('student_id', Integer, ForeignKey('students.id'), primary_key=True),
    Column('group_id', Integer, ForeignKey('groups.id'), primary_key=True)
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
    # Связь Many-to-Many со студентами
    students = relationship("Student", secondary=student_courses, back_populates="courses")


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
    # Связь Many-to-Many с кураторами
    curators = relationship("Curator", secondary=curator_groups, back_populates="groups")
    # Связь Many-to-Many с учителями
    teachers = relationship("Teacher", secondary=teacher_groups, back_populates="groups")
    # Связь Many-to-Many со студентами
    students = relationship("Student", secondary=student_groups, back_populates="groups")


# Модель студента
class Student(Base):
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    tariff = Column(String(50), nullable=True)  # 'standard' или 'premium'
    points = Column(Integer, default=0)
    coins = Column(Integer, default=0)  # Монеты для покупок в магазине
    level = Column(String(50), default='Новичок')
    created_at = Column(DateTime, server_default=func.now())

    # Связи
    user = relationship("User", backref="student_profile")
    # Связь Many-to-Many с курсами
    courses = relationship("Course", secondary=student_courses, back_populates="students")
    # Связь Many-to-Many с группами
    groups = relationship("Group", secondary=student_groups, back_populates="students")


# Модель куратора
class Curator(Base):
    __tablename__ = 'curators'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    course_id = Column(Integer, ForeignKey('courses.id', ondelete='SET NULL'), nullable=True)
    subject_id = Column(Integer, ForeignKey('subjects.id', ondelete='SET NULL'), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    # Связи
    user = relationship("User", backref="curator_profile")
    course = relationship("Course", backref="curators")
    subject = relationship("Subject", backref="curators")
    # Связь Many-to-Many с группами
    groups = relationship("Group", secondary=curator_groups, back_populates="curators")


# Модель преподавателя
class Teacher(Base):
    __tablename__ = 'teachers'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    course_id = Column(Integer, ForeignKey('courses.id', ondelete='SET NULL'), nullable=True)
    subject_id = Column(Integer, ForeignKey('subjects.id', ondelete='SET NULL'), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    # Связи
    user = relationship("User", backref="teacher_profile")
    course = relationship("Course", backref="teachers")
    subject = relationship("Subject", backref="teachers")
    # Связь Many-to-Many с группами
    groups = relationship("Group", secondary=teacher_groups, back_populates="teachers")


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
    course_id = Column(Integer, ForeignKey('courses.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    # Связи
    subject = relationship("Subject", backref="lessons")
    course = relationship("Course", backref="lessons")

    # Уникальность: одно название урока на курс и предмет
    __table_args__ = (
        UniqueConstraint('name', 'subject_id', 'course_id', name='unique_lesson_per_course_subject'),
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


# Модель теста месяца
class MonthTest(Base):
    __tablename__ = 'month_tests'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)  # Название теста
    test_type = Column(String(50), nullable=False, default='entry')  # 'entry' или 'control'
    course_id = Column(Integer, ForeignKey('courses.id', ondelete='CASCADE'), nullable=False)
    subject_id = Column(Integer, ForeignKey('subjects.id', ondelete='CASCADE'), nullable=False)
    parent_test_id = Column(Integer, ForeignKey('month_tests.id', ondelete='CASCADE'), nullable=True)  # Для контрольных тестов
    created_at = Column(DateTime, server_default=func.now())

    # Связи
    course = relationship("Course", backref="month_tests")
    subject = relationship("Subject", backref="month_tests")
    microtopics = relationship("MonthTestMicrotopic", back_populates="month_test", cascade="all, delete-orphan")

    # Связь для контрольных тестов
    parent_test = relationship("MonthTest", remote_side=[id], backref="control_tests")

    # Уникальность: один тест месяца на курс/предмет/название/тип
    __table_args__ = (
        UniqueConstraint('name', 'test_type', 'course_id', 'subject_id', name='unique_month_test_per_course_subject_type'),
    )


# Модель связи тестов месяца с микротемами
class MonthTestMicrotopic(Base):
    __tablename__ = 'month_test_microtopics'

    id = Column(Integer, primary_key=True)
    month_test_id = Column(Integer, ForeignKey('month_tests.id', ondelete='CASCADE'), nullable=False)
    microtopic_number = Column(Integer, nullable=False)  # Номер микротемы в рамках предмета
    created_at = Column(DateTime, server_default=func.now())

    # Связи
    month_test = relationship("MonthTest", back_populates="microtopics")

    # Уникальность: одна микротема на тест месяца
    __table_args__ = (
        UniqueConstraint('month_test_id', 'microtopic_number', name='unique_microtopic_per_month_test'),
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


# Модель результата домашнего задания
class HomeworkResult(Base):
    __tablename__ = 'homework_results'

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    homework_id = Column(Integer, ForeignKey('homeworks.id', ondelete='CASCADE'), nullable=False)
    total_questions = Column(Integer, nullable=False)
    correct_answers = Column(Integer, nullable=False, default=0)
    points_earned = Column(Integer, nullable=False, default=0)  # Баллы за прохождение (3 за вопрос если 100%)
    is_first_attempt = Column(Boolean, default=True)  # Первая попытка или повторная
    points_awarded = Column(Boolean, default=False)  # Были ли начислены баллы за это ДЗ
    completed_at = Column(DateTime, server_default=func.now())
    created_at = Column(DateTime, server_default=func.now())

    # Связи
    student = relationship("Student", backref="homework_results")
    homework = relationship("Homework", backref="results")
    question_results = relationship("QuestionResult", back_populates="homework_result", cascade="all, delete-orphan")


# Модель результата ответа на вопрос
class QuestionResult(Base):
    __tablename__ = 'question_results'

    id = Column(Integer, primary_key=True)
    homework_result_id = Column(Integer, ForeignKey('homework_results.id', ondelete='CASCADE'), nullable=False)
    question_id = Column(Integer, ForeignKey('questions.id', ondelete='CASCADE'), nullable=False)
    selected_answer_id = Column(Integer, ForeignKey('answer_options.id', ondelete='SET NULL'), nullable=True)
    is_correct = Column(Boolean, nullable=False)
    time_spent = Column(Integer, nullable=True)  # Время в секундах
    microtopic_number = Column(Integer, nullable=True)  # Номер микротемы для статистики понимания
    created_at = Column(DateTime, server_default=func.now())

    # Связи
    homework_result = relationship("HomeworkResult", back_populates="question_results")
    question = relationship("Question", backref="results")
    selected_answer = relationship("AnswerOption", backref="question_results")


# Модель результата входного теста курса
class CourseEntryTestResult(Base):
    __tablename__ = 'course_entry_test_results'

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    subject_id = Column(Integer, ForeignKey('subjects.id', ondelete='CASCADE'), nullable=False)
    total_questions = Column(Integer, nullable=False, default=30)  # Всегда 30 вопросов
    correct_answers = Column(Integer, nullable=False, default=0)
    score_percentage = Column(Integer, nullable=False, default=0)  # Процент правильных ответов
    completed_at = Column(DateTime, server_default=func.now())
    created_at = Column(DateTime, server_default=func.now())

    # Связи
    student = relationship("Student", backref="course_entry_test_results")
    subject = relationship("Subject", backref="course_entry_test_results")
    question_results = relationship("CourseEntryQuestionResult", back_populates="test_result", cascade="all, delete-orphan")

    # Уникальность: один результат входного теста курса на студента/предмет
    __table_args__ = (
        UniqueConstraint('student_id', 'subject_id', name='unique_course_entry_test_per_student_subject'),
    )


# Модель результата ответа на вопрос входного теста курса
class CourseEntryQuestionResult(Base):
    __tablename__ = 'course_entry_question_results'

    id = Column(Integer, primary_key=True)
    test_result_id = Column(Integer, ForeignKey('course_entry_test_results.id', ondelete='CASCADE'), nullable=False)
    question_id = Column(Integer, ForeignKey('questions.id', ondelete='CASCADE'), nullable=False)  # Ссылка на исходный вопрос
    selected_answer_id = Column(Integer, ForeignKey('answer_options.id', ondelete='SET NULL'), nullable=True)
    is_correct = Column(Boolean, nullable=False)
    time_spent = Column(Integer, nullable=True)  # Время в секундах
    microtopic_number = Column(Integer, nullable=True)  # Номер микротемы для статистики
    created_at = Column(DateTime, server_default=func.now())

    # Связи
    test_result = relationship("CourseEntryTestResult", back_populates="question_results")
    question = relationship("Question", backref="course_entry_results")
    selected_answer = relationship("AnswerOption", backref="course_entry_results")


# Модель результата входного теста месяца
class MonthEntryTestResult(Base):
    __tablename__ = 'month_entry_test_results'

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    month_test_id = Column(Integer, ForeignKey('month_tests.id', ondelete='CASCADE'), nullable=False)
    total_questions = Column(Integer, nullable=False)  # Количество вопросов (3 * количество микротем)
    correct_answers = Column(Integer, nullable=False, default=0)
    score_percentage = Column(Integer, nullable=False, default=0)  # Процент правильных ответов
    completed_at = Column(DateTime, server_default=func.now())
    created_at = Column(DateTime, server_default=func.now())

    # Связи
    student = relationship("Student", backref="month_entry_test_results")
    month_test = relationship("MonthTest", backref="month_entry_test_results")
    question_results = relationship("MonthEntryQuestionResult", back_populates="test_result", cascade="all, delete-orphan")

    # Уникальность: один результат входного теста месяца на студента/тест
    __table_args__ = (
        UniqueConstraint('student_id', 'month_test_id', name='unique_month_entry_test_per_student_test'),
    )


# Модель результата ответа на вопрос входного теста месяца
class MonthEntryQuestionResult(Base):
    __tablename__ = 'month_entry_question_results'

    id = Column(Integer, primary_key=True)
    test_result_id = Column(Integer, ForeignKey('month_entry_test_results.id', ondelete='CASCADE'), nullable=False)
    question_id = Column(Integer, ForeignKey('questions.id', ondelete='CASCADE'), nullable=False)  # Ссылка на исходный вопрос
    selected_answer_id = Column(Integer, ForeignKey('answer_options.id', ondelete='SET NULL'), nullable=True)
    is_correct = Column(Boolean, nullable=False)
    time_spent = Column(Integer, nullable=True)  # Время в секундах
    microtopic_number = Column(Integer, nullable=True)  # Номер микротемы для статистики
    created_at = Column(DateTime, server_default=func.now())

    # Связи
    test_result = relationship("MonthEntryTestResult", back_populates="question_results")
    question = relationship("Question", backref="month_entry_results")
    selected_answer = relationship("AnswerOption", backref="month_entry_results")


# Модель результата контрольного теста месяца
class MonthControlTestResult(Base):
    __tablename__ = 'month_control_test_results'

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    month_test_id = Column(Integer, ForeignKey('month_tests.id', ondelete='CASCADE'), nullable=False)
    total_questions = Column(Integer, nullable=False)  # Количество вопросов (3 * количество микротем)
    correct_answers = Column(Integer, nullable=False, default=0)
    score_percentage = Column(Integer, nullable=False, default=0)  # Процент правильных ответов
    completed_at = Column(DateTime, server_default=func.now())
    created_at = Column(DateTime, server_default=func.now())

    # Связи
    student = relationship("Student", backref="month_control_test_results")
    month_test = relationship("MonthTest", backref="month_control_test_results")
    question_results = relationship("MonthControlQuestionResult", back_populates="test_result", cascade="all, delete-orphan")

    # Уникальность: один результат контрольного теста месяца на студента/тест
    __table_args__ = (
        UniqueConstraint('student_id', 'month_test_id', name='unique_month_control_test_per_student_test'),
    )


# Модель результата ответа на вопрос контрольного теста месяца
class MonthControlQuestionResult(Base):
    __tablename__ = 'month_control_question_results'

    id = Column(Integer, primary_key=True)
    test_result_id = Column(Integer, ForeignKey('month_control_test_results.id', ondelete='CASCADE'), nullable=False)
    question_id = Column(Integer, ForeignKey('questions.id', ondelete='CASCADE'), nullable=False)  # Ссылка на исходный вопрос
    selected_answer_id = Column(Integer, ForeignKey('answer_options.id', ondelete='SET NULL'), nullable=True)
    is_correct = Column(Boolean, nullable=False)
    time_spent = Column(Integer, nullable=True)  # Время в секундах
    microtopic_number = Column(Integer, nullable=True)  # Номер микротемы для статистики
    created_at = Column(DateTime, server_default=func.now())

    # Связи
    test_result = relationship("MonthControlTestResult", back_populates="question_results")
    question = relationship("Question", backref="month_control_results")
    selected_answer = relationship("AnswerOption", backref="month_control_results")







# Модель товара в магазине
class ShopItem(Base):
    __tablename__ = 'shop_items'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Integer, nullable=False)  # Цена в монетах
    item_type = Column(String(50), nullable=False)  # 'bonus_test', 'pdf', 'money', 'other'
    content = Column(Text, nullable=True)  # Реальный контент товара (текст задания, ссылки, инструкции)
    file_path = Column(String(500), nullable=True)  # Путь к файлу (для PDF и других файлов)
    contact_info = Column(Text, nullable=True)  # Контактная информация (для консультаций, получения призов)
    is_active = Column(Boolean, default=True)  # Активен ли товар
    created_at = Column(DateTime, server_default=func.now())

    # Связи
    purchases = relationship("StudentPurchase", back_populates="item", cascade="all, delete-orphan")


# Модель покупки студента
class StudentPurchase(Base):
    __tablename__ = 'student_purchases'

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    item_id = Column(Integer, ForeignKey('shop_items.id', ondelete='CASCADE'), nullable=False)
    price_paid = Column(Integer, nullable=False)  # Цена на момент покупки
    is_used = Column(Boolean, default=False)  # Использован ли товар (для бонусных тестов)
    purchased_at = Column(DateTime, server_default=func.now())

    # Связи
    student = relationship("Student", backref="purchases")
    item = relationship("ShopItem", back_populates="purchases")


# Модель результата пробного ЕНТ
class TrialEntResult(Base):
    __tablename__ = 'trial_ent_results'

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    # Выбранные предметы (JSON строка с кодами предметов)
    required_subjects = Column(Text, nullable=False)  # JSON: ["kz", "mathlit"] или ["kz"] или ["mathlit"]
    profile_subjects = Column(Text, nullable=False)   # JSON: ["math", "geo"] или [] или ["bio", "chem"]
    total_questions = Column(Integer, nullable=False)
    correct_answers = Column(Integer, nullable=False, default=0)
    completed_at = Column(DateTime, server_default=func.now())
    created_at = Column(DateTime, server_default=func.now())

    # Связи
    student = relationship("Student", backref="trial_ent_results")
    question_results = relationship("TrialEntQuestionResult", back_populates="test_result", cascade="all, delete-orphan")


# Модель результата ответа на вопрос пробного ЕНТ
class TrialEntQuestionResult(Base):
    __tablename__ = 'trial_ent_question_results'

    id = Column(Integer, primary_key=True)
    test_result_id = Column(Integer, ForeignKey('trial_ent_results.id', ondelete='CASCADE'), nullable=False)
    question_id = Column(Integer, ForeignKey('questions.id', ondelete='CASCADE'), nullable=False)  # Ссылка на исходный вопрос
    selected_answer_id = Column(Integer, ForeignKey('answer_options.id', ondelete='SET NULL'), nullable=True)
    is_correct = Column(Boolean, nullable=False)
    subject_code = Column(String(20), nullable=False)  # kz, mathlit, math, geo, bio, chem, inf, world
    time_spent = Column(Integer, nullable=True)  # Время в секундах
    microtopic_number = Column(Integer, nullable=True)  # Номер микротемы для статистики
    created_at = Column(DateTime, server_default=func.now())

    # Связи
    test_result = relationship("TrialEntResult", back_populates="question_results")
    question = relationship("Question", backref="trial_ent_results")
    selected_answer = relationship("AnswerOption", backref="trial_ent_results")


# Модель покупки бонусного теста студентом
class StudentBonusTest(Base):
    __tablename__ = 'student_bonus_tests'

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    bonus_test_id = Column(Integer, ForeignKey('bonus_tests.id', ondelete='CASCADE'), nullable=False)
    price_paid = Column(Integer, nullable=False)  # Цена на момент покупки
    is_used = Column(Boolean, default=False)  # Пройден ли тест
    purchased_at = Column(DateTime, server_default=func.now())

    # Связи
    student = relationship("Student", backref="bonus_tests")
    bonus_test = relationship("BonusTest", backref="student_purchases")
