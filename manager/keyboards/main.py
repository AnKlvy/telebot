from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_manager_main_menu_kb() -> InlineKeyboardMarkup:
    """Клавиатура главного меню менеджера"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Аналитика", callback_data="manager_analytics")],
        [InlineKeyboardButton(text="➕ Добавить ДЗ", callback_data="manager_add_homework")],
        [InlineKeyboardButton(text="➕ Добавить микротему", callback_data="manager_add_topic")],
        [InlineKeyboardButton(text="➕ Добавить урок", callback_data="manager_add_lesson")],
        [InlineKeyboardButton(text="🧪 Бонусный тест", callback_data="manager_bonus_test")],
        [InlineKeyboardButton(text="🎯 Бонусное задание", callback_data="manager_bonus_task")],
        [InlineKeyboardButton(text="🧠 Входной и контрольный месяца", callback_data="manager_tests")]
    ])