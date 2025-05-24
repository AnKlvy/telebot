from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from common.keyboards import get_universal_back_button

def get_account_kb() -> InlineKeyboardMarkup:
    """Клавиатура для раздела аккаунта"""
    return InlineKeyboardMarkup(inline_keyboard=[
        get_universal_back_button("🏠 Главное меню", "back_to_main")
    ])