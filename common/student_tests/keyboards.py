from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List

from common.keyboards import get_main_menu_back_button


def get_test_subjects_kb(test_type: str) -> InlineKeyboardMarkup:
    """
    Клавиатура с предметами для тестов
    
    Args:
        test_type: Тип теста (course_entry, month_entry, month_control)
    """
    subjects = [
        {"id": "kz", "name": "История Казахстана"},
        {"id": "mathlit", "name": "Математическая грамотность"},
        {"id": "math", "name": "Математика"},
        {"id": "geo", "name": "География"},
        {"id": "bio", "name": "Биология"},
        {"id": "chem", "name": "Химия"},
        {"id": "inf", "name": "Информатика"},
        {"id": "world", "name": "Всемирная история"}
    ]
    
    buttons = []
    for subject in subjects:
        buttons.append([
            InlineKeyboardButton(
                text=subject["name"],
                callback_data=f"{test_type}_sub_{subject['id']}"
            )
        ])
    
    # Добавляем кнопку "Назад"
    buttons.extend(get_main_menu_back_button())
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_month_test_kb(test_type: str, subject_id: str) -> InlineKeyboardMarkup:
    """
    Клавиатура с месяцами для тестов
    
    Args:
        test_type: Тип теста (month_entry, month_control)
        subject_id: ID предмета
    """
    months = [
        {"id": "1", "name": "Сентябрь"},
        {"id": "2", "name": "Октябрь"},
        {"id": "3", "name": "Ноябрь"},
        {"id": "4", "name": "Декабрь"},
        {"id": "5", "name": "Январь"},
        {"id": "6", "name": "Февраль"},
        {"id": "7", "name": "Март"},
        {"id": "8", "name": "Апрель"},
        {"id": "9", "name": "Май"}
    ]
    
    buttons = []
    for month in months:
        buttons.append([
            InlineKeyboardButton(
                text=month["name"],
                callback_data=f"{test_type}_{subject_id}_month_{month['id']}"
            )
        ])
    
    # Добавляем кнопку "Назад"
    back_action = "back_to_month_entry_subjects" if test_type == "month_entry" else "back_to_month_control_subjects"
    buttons.append([
        InlineKeyboardButton(
            text="◀️ Назад",
            callback_data=back_action
        )
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_test_answers_kb() -> InlineKeyboardMarkup:
    """Клавиатура с вариантами ответов на вопрос теста"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="A", callback_data="answer_A")],
        [InlineKeyboardButton(text="B", callback_data="answer_B")],
        [InlineKeyboardButton(text="C", callback_data="answer_C")],
        [InlineKeyboardButton(text="D", callback_data="answer_D")],
        *get_main_menu_back_button()
    ])

def get_back_to_test_kb() -> InlineKeyboardMarkup:
    """Клавиатура для возврата в меню тестов"""
    return InlineKeyboardMarkup(inline_keyboard=[
        *get_main_menu_back_button()
    ]
    )

def get_tests_menu_kb() -> InlineKeyboardMarkup:
    """Клавиатура главного меню тестов"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Входной тест курса", callback_data="course_entry_test")],
        [InlineKeyboardButton(text="📊 Входной тест месяца", callback_data="month_entry_test")],
        [InlineKeyboardButton(text="📈 Контрольный тест месяца", callback_data="month_control_test")],
        *get_main_menu_back_button()
    ])