from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from common.keyboards import get_main_menu_back_button

def get_manager_analytics_menu_kb() -> InlineKeyboardMarkup:
    """Клавиатура меню аналитики менеджера"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Статистика по ученику", callback_data="student_analytics")],
        [InlineKeyboardButton(text="📈 Статистика по группе", callback_data="group_analytics")],
        [InlineKeyboardButton(text="📚 Статистика по предмету", callback_data="subject_analytics")],
        [InlineKeyboardButton(text="📋 Общая статистика", callback_data="general_analytics")],
        *get_main_menu_back_button()
    ])

def get_curators_kb() -> InlineKeyboardMarkup:
    """Клавиатура выбора куратора"""
    # В реальном приложении здесь будет запрос к базе данных
    curators = [
        {"id": "curator1", "name": "Иванов И.И."},
        {"id": "curator2", "name": "Петров П.П."},
        {"id": "curator3", "name": "Сидоров С.С."}
    ]
    
    buttons = []
    for curator in curators:
        buttons.append([
            InlineKeyboardButton(
                text=curator["name"], 
                callback_data=f"manager_curator_{curator['id']}"
            )
        ])
    
    buttons.extend(get_main_menu_back_button())
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_subjects_kb() -> InlineKeyboardMarkup:
    """Клавиатура выбора предмета"""
    # В реальном приложении здесь будет запрос к базе данных
    subjects = [
        {"id": "subject1", "name": "Математика"},
        {"id": "subject2", "name": "Физика"},
        {"id": "subject3", "name": "Химия"},
        {"id": "subject4", "name": "Биология"}
    ]
    
    buttons = []
    for subject in subjects:
        buttons.append([
            InlineKeyboardButton(
                text=subject["name"], 
                callback_data=f"manager_subject_{subject['id']}"
            )
        ])
    
    buttons.extend(get_main_menu_back_button())
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)