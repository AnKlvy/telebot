from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_teacher_main_menu_kb() -> InlineKeyboardMarkup:
    """Клавиатура главного меню преподавателя"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👥 Моя группа", callback_data="teacher_my_group")],
        [InlineKeyboardButton(text="📊 Аналитика", callback_data="teacher_analytics")],
        [InlineKeyboardButton(text="🧠 Тесты", callback_data="teacher_tests")]
    ])