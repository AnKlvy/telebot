from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from common.keyboards import get_main_menu_back_button

def get_analytics_menu_kb(role: str) -> InlineKeyboardMarkup:
    """Клавиатура меню аналитики"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Статистика по ученику", callback_data="student_analytics")],
        [InlineKeyboardButton(text="📈 Статистика по группе", callback_data="group_analytics")],
        *get_main_menu_back_button()
    ])

def get_groups_for_analytics_kb(role: str) -> InlineKeyboardMarkup:
    """Клавиатура выбора группы для аналитики"""
    # В реальном приложении здесь будет запрос к базе данных
    groups = [
        {"id": "group1", "name": "Интенсив. География"},
        {"id": "group2", "name": "Интенсив. Математика"}
    ]
    
    buttons = []
    for group in groups:
        buttons.append([
            InlineKeyboardButton(
                text=group["name"], 
                callback_data=f"analytics_group_{group['id']}"
            )
        ])
    
    buttons.extend(get_main_menu_back_button())
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_students_for_analytics_kb(group_id: str) -> InlineKeyboardMarkup:
    """Клавиатура выбора ученика для аналитики"""
    # В реальном приложении здесь будет запрос к базе данных
    students = {
        "group1": [
            {"id": "student1", "name": "Мадияр Сапаров"},
            {"id": "student2", "name": "Аружан Ахметова"}
        ],
        "group2": [
            {"id": "student3", "name": "Диана Нурланова"},
            {"id": "student4", "name": "Арман Сериков"}
        ]
    }
    
    group_students = students.get(group_id, [])
    
    buttons = []
    for student in group_students:
        buttons.append([
            InlineKeyboardButton(
                text=student["name"], 
                callback_data=f"analytics_student_{student['id']}"
            )
        ])
    
    buttons.extend(get_main_menu_back_button())
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_back_to_analytics_kb() -> InlineKeyboardMarkup:
    """Клавиатура возврата в меню аналитики"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад к аналитике", callback_data="back_to_analytics")],
        *get_main_menu_back_button()
    ])