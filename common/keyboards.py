from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Dict, Any, Tuple


async def get_courses_kb() -> InlineKeyboardMarkup:
    """Общая клавиатура выбора курса с данными из БД"""
    try:
        from database import CourseRepository
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
        print(f"Ошибка при получении курсов: {e}")
        # В случае ошибки показываем сообщение об ошибке
        buttons = [
            [InlineKeyboardButton(text="❌ Ошибка загрузки курсов", callback_data="courses_error")],
            *get_main_menu_back_button()
        ]
        return InlineKeyboardMarkup(inline_keyboard=buttons)

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
        *get_main_menu_back_button()
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
    
    buttons.extend(get_main_menu_back_button())
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_home_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[back_to_main_button()])

def get_home_and_back_kb() -> InlineKeyboardMarkup:
    """Кнопка возврата в главное меню и назад"""
    return InlineKeyboardMarkup(inline_keyboard=[
        *get_main_menu_back_button()
    ])


def get_universal_back_button(text: str = "⬅️ Назад", callback_data: str = "back") -> List[InlineKeyboardButton]:
    """
    Универсальная кнопка назад с настраиваемым текстом и callback_data
    
    Args:
        text (str): Текст кнопки (по умолчанию "⬅️ Назад")
        callback_data (str): Данные для callback (по умолчанию "back")
        
    Returns:
        List[InlineKeyboardButton]: Список с одной кнопкой назад
    """
    return [InlineKeyboardButton(text=text, callback_data=callback_data)]
def back_to_main_button() -> List[InlineKeyboardButton]:
    return get_universal_back_button("🏠 Главное меню", "back_to_main")

def get_main_menu_back_button() -> list[list[InlineKeyboardButton]]:
    """Кнопка возврата в главное меню"""
    return [get_universal_back_button(), get_universal_back_button("🏠 Главное меню", "back_to_main")]

