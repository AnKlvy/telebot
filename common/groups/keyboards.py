from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from common.keyboards import get_main_menu_back_button

def get_groups_kb(role: str) -> InlineKeyboardMarkup:
    """Клавиатура выбора группы"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📗 Химия — Премиум", callback_data=f"{role}_group_chem_premium")],
        [InlineKeyboardButton(text="📘 Биология — Интенсив", callback_data=f"{role}_group_bio_intensive")],
        [InlineKeyboardButton(text="📕 История — Базовый", callback_data=f"{role}_group_history_basic")],
        *get_main_menu_back_button()
    ])

def get_students_kb(role: str, group_id: str) -> InlineKeyboardMarkup:
    """Клавиатура выбора ученика в группе"""
    buttons = [
        [InlineKeyboardButton(text="👤 Аружан Ахметова", callback_data=f"{role}_student_1")],
        [InlineKeyboardButton(text="👤 Мадияр Сапаров", callback_data=f"{role}_student_2")],
        [InlineKeyboardButton(text="👤 Диана Ержанова", callback_data=f"{role}_student_3")],
        *get_main_menu_back_button()
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_student_profile_kb(role: str) -> InlineKeyboardMarkup:
    """Клавиатура для карточки ученика"""
    return InlineKeyboardMarkup(inline_keyboard=[
        *get_main_menu_back_button()
    ])