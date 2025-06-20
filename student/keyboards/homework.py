from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from common.keyboards import get_main_menu_back_button
from database import LessonRepository, SubjectRepository, CourseRepository

async def get_courses_kb(user_id: int = None) -> InlineKeyboardMarkup:
    """Клавиатура выбора курса с реальными данными из БД"""
    try:
        if user_id:
            # Получаем только курсы студента
            courses = await CourseRepository.get_by_user_id(user_id)
        else:
            # Получаем все курсы (для обратной совместимости)
            courses = await CourseRepository.get_all()

        buttons = []

        for course in courses:
            buttons.append([
                InlineKeyboardButton(
                    text=course.name,
                    callback_data=f"course_{course.id}"
                )
            ])

        if not courses:
            buttons.append([
                InlineKeyboardButton(text="❌ Нет доступных курсов", callback_data="no_courses")
            ])

        buttons.extend(get_main_menu_back_button())
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    except Exception as e:
        # В случае ошибки показываем сообщение об ошибке, а не захардкоженные данные
        print(f"Ошибка при получении курсов: {e}")
        buttons = [
            [InlineKeyboardButton(text="❌ Ошибка загрузки курсов", callback_data="courses_error")],
            *get_main_menu_back_button()
        ]
        return InlineKeyboardMarkup(inline_keyboard=buttons)

async def get_subjects_kb(course_id: int = None, user_id: int = None) -> InlineKeyboardMarkup:
    """Клавиатура выбора предмета с реальными данными из БД"""
    try:
        if course_id:
            # Получаем предметы для конкретного курса
            course = await CourseRepository.get_by_id(course_id)
            subjects = course.subjects if course else []
        elif user_id:
            # Получаем уникальные предметы студента из всех его курсов
            subjects = await SubjectRepository.get_by_user_id(user_id)
        else:
            # Получаем все предметы
            subjects = await SubjectRepository.get_all()

        buttons = []
        for subject in subjects:
            buttons.append([
                InlineKeyboardButton(
                    text=subject.name,
                    callback_data=f"subject_{subject.id}"
                )
            ])

        if not subjects:
            buttons.append([
                InlineKeyboardButton(text="❌ Нет доступных предметов", callback_data="no_subjects")
            ])

        buttons.extend(get_main_menu_back_button())
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    except Exception as e:
        # В случае ошибки показываем сообщение об ошибке
        print(f"Ошибка при получении предметов: {e}")
        buttons = [
            [InlineKeyboardButton(text="❌ Ошибка загрузки предметов", callback_data="subjects_error")],
            *get_main_menu_back_button()
        ]
        return InlineKeyboardMarkup(inline_keyboard=buttons)

async def get_lessons_kb(subject_id: int = None, course_id: int = None) -> InlineKeyboardMarkup:
    """Клавиатура выбора урока с реальными данными из БД"""
    try:
        if subject_id and course_id:
            # Получаем уроки для конкретного предмета и курса
            lessons = await LessonRepository.get_by_subject_and_course(subject_id, course_id)
        elif subject_id:
            # Для обратной совместимости - получаем все уроки предмета
            lessons = await LessonRepository.get_by_subject(subject_id)
        else:
            # Если ничего не указано, показываем все уроки
            lessons = await LessonRepository.get_all()

        buttons = []
        for lesson in lessons:
            buttons.append([
                InlineKeyboardButton(
                    text=lesson.name,
                    callback_data=f"lesson_{lesson.id}"
                )
            ])

        buttons.extend(get_main_menu_back_button())
        return InlineKeyboardMarkup(inline_keyboard=buttons)

    except Exception as e:
        # В случае ошибки возвращаем пустую клавиатуру с кнопкой назад
        return InlineKeyboardMarkup(inline_keyboard=[
            *get_main_menu_back_button()
        ])

def get_homeworks_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Базовое", callback_data="homework_basic")],
        [InlineKeyboardButton(text="Углублённое", callback_data="homework_advanced")],
        [InlineKeyboardButton(text="Повторение", callback_data="homework_review")],
        *get_main_menu_back_button()
    ])

def get_confirm_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="▶️ Начать тест", callback_data="start_test")],
        *get_main_menu_back_button()
    ])

def get_test_answers_kb() -> InlineKeyboardMarkup:
    """Клавиатура с вариантами ответов на вопрос теста"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="A", callback_data="answer_A")],
        [InlineKeyboardButton(text="B", callback_data="answer_B")],
        [InlineKeyboardButton(text="C", callback_data="answer_C")],
        [InlineKeyboardButton(text="D", callback_data="answer_D")]
    ])

def get_after_test_kb() -> InlineKeyboardMarkup:
    """Клавиатура после завершения теста"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Пройти ещё раз", callback_data="retry_test")],
        [InlineKeyboardButton(text="📊 Мой прогресс", callback_data="progress")],
        *get_main_menu_back_button()
    ])

