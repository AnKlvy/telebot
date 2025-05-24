from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from common.keyboards import get_main_menu_back_button


def get_curator_groups_kb() -> InlineKeyboardMarkup:
    """Клавиатура выбора группы куратора"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📗 Химия — Премиум", callback_data="group_chem_premium")],
        [InlineKeyboardButton(text="📘 Биология — Интенсив", callback_data="group_bio_intensive")],
        [InlineKeyboardButton(text="📕 История — Базовый", callback_data="group_history_basic")],
        *get_main_menu_back_button()
    ])


def get_group_students_kb(group_id: str) -> InlineKeyboardMarkup:
    """Клавиатура выбора ученика в группе"""
    # Упрощаем структуру - используем только ID студента в callback_data
    buttons = [
        [InlineKeyboardButton(text="👤 Аружан Ахметова", callback_data="student_1")],
        [InlineKeyboardButton(text="👤 Мадияр Сапаров", callback_data="student_2")],
        [InlineKeyboardButton(text="👤 Диана Ержанова", callback_data="student_3")],
        *get_main_menu_back_button()
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_student_profile_kb() -> InlineKeyboardMarkup:
    """Клавиатура для карточки ученика"""
    return InlineKeyboardMarkup(inline_keyboard=[
        *get_main_menu_back_button()
    ])
