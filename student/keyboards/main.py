from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_student_main_menu_kb() -> InlineKeyboardMarkup:
    """Клавиатура главного меню студента"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Домашнее задание", callback_data="homework")],
        [InlineKeyboardButton(text="📊 Мой прогресс", callback_data="progress")],
        [InlineKeyboardButton(text="🎁 Магазин", callback_data="shop")],
        [InlineKeyboardButton(text="🧠 Тест-отчет", callback_data="test_report")],
        [InlineKeyboardButton(text="🧪 Пробный ЕНТ", callback_data="trial_ent")],
        [InlineKeyboardButton(text="📞 Связь с куратором", callback_data="curator")],
        [InlineKeyboardButton(text="❓ Аккаунт", callback_data="account")]
    ])