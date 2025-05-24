from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from common.keyboards import get_main_menu_back_button

def get_progress_menu_kb() -> InlineKeyboardMarkup:
    """Клавиатура меню прогресса"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Общая статистика", callback_data="general_stats")],
        [InlineKeyboardButton(text="📈 Понимание по темам", callback_data="topics_understanding")],
         *get_main_menu_back_button()
    ])

def get_subjects_progress_kb() -> InlineKeyboardMarkup:
    """Клавиатура выбора предмета для просмотра прогресса"""
    buttons = [
        [InlineKeyboardButton(text="История Казахстана", callback_data="progress_sub_kz")],
        [InlineKeyboardButton(text="Математическая грамотность", callback_data="progress_sub_mathlit")],
        [InlineKeyboardButton(text="Математика", callback_data="progress_sub_math")],
        [InlineKeyboardButton(text="География", callback_data="progress_sub_geo")],
        [InlineKeyboardButton(text="Биология", callback_data="progress_sub_bio")],
        [InlineKeyboardButton(text="Химия", callback_data="progress_sub_chem")],
        [InlineKeyboardButton(text="Информатика", callback_data="progress_sub_inf")],
        [InlineKeyboardButton(text="Всемирная история", callback_data="progress_sub_world")],
        [InlineKeyboardButton(text="Грамотность чтения", callback_data="progress_sub_read")],
        *get_main_menu_back_button()
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_back_to_progress_kb() -> InlineKeyboardMarkup:
    """Клавиатура для возврата в меню прогресса"""
    return InlineKeyboardMarkup(inline_keyboard=[
        *get_main_menu_back_button()
    ])