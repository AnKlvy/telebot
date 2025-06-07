from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_manager_main_menu_kb() -> InlineKeyboardMarkup:
    """Клавиатура главного меню менеджера"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Аналитика", callback_data="manager_analytics")],
        [InlineKeyboardButton(text="📚 ДЗ", callback_data="manager_homework")],
        [InlineKeyboardButton(text="📝 Микротемы", callback_data="manager_topics")],
        [InlineKeyboardButton(text="📖 Уроки", callback_data="manager_lessons")],
        [InlineKeyboardButton(text="🧪 Бонусный тест", callback_data="manager_bonus_test")],
        [InlineKeyboardButton(text="🎯 Бонусное задание", callback_data="manager_bonus_tasks")],
        [InlineKeyboardButton(text="🧠 Входной и контрольный месяца", callback_data="manager_tests")]
    ])