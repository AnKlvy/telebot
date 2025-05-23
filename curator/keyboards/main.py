from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_curator_main_menu_kb() -> InlineKeyboardMarkup:
    """Клавиатура главного меню куратора"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👥 Моя группа", callback_data="curator_my_group")],
        [InlineKeyboardButton(text="✅ Домашние задания", callback_data="curator_homeworks")],
        [InlineKeyboardButton(text="📩 Связь с учениками", callback_data="curator_messages")],
        [InlineKeyboardButton(text="📊 Аналитика", callback_data="curator_analytics")],
        [InlineKeyboardButton(text="🧠 Тесты", callback_data="curator_tests")]
    ])