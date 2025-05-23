from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Dict, Any

def get_courses_kb() -> InlineKeyboardMarkup:
    """Общая клавиатура выбора курса"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Интенсив. География", callback_data="course_geo")],
        [InlineKeyboardButton(text="Интенсив. Математика", callback_data="course_math")],
        get_universal_back_button()
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
        get_universal_back_button()
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
    
    buttons.append(get_universal_back_button())
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_universal_back_button(text: str = "⬅️ Назад", callback_data: str = "back_to_previous") -> List[InlineKeyboardButton]:
    """
    Универсальная кнопка назад с настраиваемым текстом и callback_data
    
    Args:
        text (str): Текст кнопки (по умолчанию "⬅️ Назад")
        callback_data (str): Данные для callback (по умолчанию "back_to_previous")
        
    Returns:
        List[InlineKeyboardButton]: Список с одной кнопкой назад
    """
    return [InlineKeyboardButton(text=text, callback_data=callback_data)]
