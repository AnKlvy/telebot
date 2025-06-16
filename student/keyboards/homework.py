from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from common.keyboards import get_main_menu_back_button
from database import LessonRepository, SubjectRepository, CourseRepository

async def get_courses_kb() -> InlineKeyboardMarkup:
    """Клавиатура выбора курса с реальными данными из БД"""
    try:
        courses = await CourseRepository.get_all()
        buttons = []

        for course in courses:
            buttons.append([
                InlineKeyboardButton(
                    text=course.name,
                    callback_data=f"course_{course.id}"
                )
            ])

        buttons.extend(get_main_menu_back_button())
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    except Exception:
        # Fallback на хардкод данные в случае ошибки
        buttons = [
            [InlineKeyboardButton(text="Интенсив. География", callback_data="course_1")],
            [InlineKeyboardButton(text="Интенсив. Математика", callback_data="course_2")],
            *get_main_menu_back_button()
        ]
        return InlineKeyboardMarkup(inline_keyboard=buttons)

async def get_subjects_kb(course_id: int = None) -> InlineKeyboardMarkup:
    """Клавиатура выбора предмета с реальными данными из БД"""
    try:
        if course_id:
            # Получаем предметы для конкретного курса
            course = await CourseRepository.get_by_id(course_id)
            subjects = course.subjects if course else []
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

        buttons.extend(get_main_menu_back_button())
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    except Exception:
        # Fallback на хардкод данные в случае ошибки
        buttons = [
            [InlineKeyboardButton(text="История Казахстана", callback_data="subject_1")],
            [InlineKeyboardButton(text="Математическая грамотность", callback_data="subject_2")],
            [InlineKeyboardButton(text="География", callback_data="subject_3")],
            [InlineKeyboardButton(text="Биология", callback_data="subject_4")],
            [InlineKeyboardButton(text="Химия", callback_data="subject_5")],
            [InlineKeyboardButton(text="Информатика", callback_data="subject_6")],
            *get_main_menu_back_button()
        ]
        return InlineKeyboardMarkup(inline_keyboard=buttons)

async def get_lessons_kb(subject_id: int = None) -> InlineKeyboardMarkup:
    """Клавиатура выбора урока с реальными данными из БД"""
    try:
        if subject_id:
            lessons = await LessonRepository.get_by_subject(subject_id)
        else:
            # Если предмет не указан, показываем все уроки (для обратной совместимости)
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

