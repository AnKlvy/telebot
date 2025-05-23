from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_curator_subjects_kb() -> InlineKeyboardMarkup:
    """Клавиатура выбора предмета для связи с куратором"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📗 Химия", callback_data="curator_chem")],
        [InlineKeyboardButton(text="📘 Биология", callback_data="curator_bio")],
        [InlineKeyboardButton(text="📕 История Казахстана", callback_data="curator_kz")],
        [InlineKeyboardButton(text="📐 Матемграмотность", callback_data="curator_mathlit")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main")]
    ])

def get_back_to_curator_kb() -> InlineKeyboardMarkup:
    """Клавиатура для возврата к выбору предмета куратора"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_curator")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main")]
    ])