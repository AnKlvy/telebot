from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData
from common.keyboards import get_main_menu_back_button
from typing import List, Literal, Dict

# Константы для действий с уроками
class LessonActions:
    VIEW = "view"
    ADD = "add"
    DELETE = "del"
    CONFIRM_DELETE = "cdel"
    CANCEL = "cancel"

class LessonCallback(CallbackData, prefix="lesson"):
    """Фабрика callback-данных для работы с уроками"""
    action: Literal[LessonActions.VIEW, LessonActions.ADD, LessonActions.DELETE,
                   LessonActions.CONFIRM_DELETE, LessonActions.CANCEL]  # Тип действия с уроком
    course_id: int | None = None  # ID курса
    subject_id: int | None = None  # ID предмета
    lesson_id: int | None = None  # ID урока

def get_lessons_menu_kb() -> InlineKeyboardMarkup:
    """Клавиатура меню уроков"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Список уроков", callback_data=LessonCallback(action=LessonActions.VIEW).pack())],
        [InlineKeyboardButton(text="➕ Добавить урок", callback_data=LessonCallback(action=LessonActions.ADD).pack())],
        [InlineKeyboardButton(text="❌ Удалить урок", callback_data=LessonCallback(action=LessonActions.DELETE).pack())],
        *get_main_menu_back_button()
    ])

def get_courses_list_kb(courses: Dict[int, str]) -> InlineKeyboardMarkup:
    """Клавиатура со списком курсов"""
    keyboard = []
    for course_id, course_name in courses.items():
        keyboard.append([
            InlineKeyboardButton(
                text=course_name,
                callback_data=LessonCallback(
                    action=LessonActions.VIEW,
                    course_id=course_id
                ).pack()
            )
        ])
    keyboard.extend(get_main_menu_back_button())
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_subjects_list_kb(subjects: List[str], course_id: int) -> InlineKeyboardMarkup:
    """Клавиатура со списком предметов"""
    keyboard = []
    for subject_id, subject_name in enumerate(subjects):
        keyboard.append([
            InlineKeyboardButton(
                text=subject_name,
                callback_data=LessonCallback(
                    action=LessonActions.VIEW,
                    course_id=course_id,
                    subject_id=subject_id
                ).pack()
            )
        ])
    keyboard.extend(get_main_menu_back_button())
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_lessons_list_kb(lessons: List[str], course_id: int | None = None, subject_id: int | None = None) -> InlineKeyboardMarkup:
    """Клавиатура со списком уроков"""
    keyboard = []
    
    # Кнопка добавления нового урока
    if course_id is not None and subject_id is not None:
        keyboard.append([
            InlineKeyboardButton(
                text="➕ Добавить урок",
                callback_data=LessonCallback(
                    action=LessonActions.ADD,
                    course_id=course_id,
                    subject_id=subject_id
                ).pack()
            )
        ])
    
    # Список существующих уроков
    for lesson_id, lesson_name in enumerate(lessons):
        keyboard.append([
            InlineKeyboardButton(
                text=f"📝 {lesson_name}",
                callback_data=LessonCallback(
                    action=LessonActions.VIEW,
                    course_id=course_id,
                    subject_id=subject_id,
                    lesson_id=lesson_id
                ).pack()
            ),
            InlineKeyboardButton(
                text="❌",
                callback_data=LessonCallback(
                    action=LessonActions.DELETE,
                    course_id=course_id,
                    subject_id=subject_id,
                    lesson_id=lesson_id
                ).pack()
            )
        ])
    
    keyboard.extend(get_main_menu_back_button())
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def confirm_delete_lesson_kb(lesson_id: int) -> InlineKeyboardMarkup:
    """Клавиатура подтверждения удаления урока"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Подтвердить",
                callback_data=LessonCallback(
                    action=LessonActions.CONFIRM_DELETE,
                    lesson_id=lesson_id
                ).pack()
            ),
            InlineKeyboardButton(
                text="❌ Отменить",
                callback_data=LessonCallback(action=LessonActions.CANCEL).pack()
            )
        ],
        *get_main_menu_back_button()
    ])