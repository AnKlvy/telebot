from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_account_kb() -> InlineKeyboardMarkup:
    """Клавиатура для раздела аккаунта"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main")]
    ])