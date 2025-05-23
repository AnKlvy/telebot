from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Dict, Any

def get_courses_kb() -> InlineKeyboardMarkup:
    """Общая клавиатура выбора курса"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Интенсив. География", callback_data="course_geo")],
        [InlineKeyboardButton(text="Интенсив. Математика", callback_data="course_math")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_previous")]
    ])

def get_subjects_kb() -> InlineKeyboardMarkup:
    """Общая клавиатура выбора предмета"""
    buttons = [
        [InlineKeyboardButton(text="История Казахстана", callback_data="subject_kz")],
        [InlineKeyboardButton(text="Математическая грамотность", callback_data="subject_mathlit")],
        [InlineKeyboardButton(text="Математика", callback_data="subject_math")],
        [InlineKeyboardButton(text="География", callback_data="subject_geo")],
        [InlineKeyboardButton(text="Биология", callback_data="subject_bio")],
        [InlineKeyboardButton(text="Химия", callback_data="subject_chem")],
        [InlineKeyboardButton(text="Информатика", callback_data="subject_inf")],
        [InlineKeyboardButton(text="Всемирная история", callback_data="subject_world")],
        [InlineKeyboardButton(text="Грамотность чтения", callback_data="subject_read")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_previous")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_lessons_kb(subject_id: str = None) -> InlineKeyboardMarkup:
    """Общая клавиатура выбора урока"""
    # В реальном приложении здесь будет запрос к базе данных
    # для получения списка уроков по конкретному предмету
    lessons = [
        {"id": "lesson1", "name": "1. Алканы"},
        {"id": "lesson2", "name": "2. Изомерия"},
        {"id": "lesson3", "name": "3. Кислоты"}
    ]
    
    buttons = []
    for lesson in lessons:
        buttons.append([
            InlineKeyboardButton(
                text=lesson["name"], 
                callback_data=f"lesson_{lesson['id']}"
            )
        ])
    
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_previous")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_universal_back_button() -> List[InlineKeyboardButton]:
    """Универсальная кнопка назад"""
    return [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_previous")]