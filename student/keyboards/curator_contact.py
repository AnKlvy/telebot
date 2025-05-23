from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_curator_subjects_kb() -> InlineKeyboardMarkup:
    """Клавиатура выбора предмета для связи с куратором"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📗 Химия", callback_data="curator_chem")],
        [InlineKeyboardButton(text="📘 Биология", callback_data="curator_bio")],
        [InlineKeyboardButton(text="📕 История Казахстана", callback_data="curator_kz")],
        [InlineKeyboardButton(text="📐 Матемграмотность", callback_data="curator_mathlit")],
        get_universal_back_button("🏠 Главное меню", "back_to_main")
    ])

def get_back_to_curator_kb() -> InlineKeyboardMarkup:
    """Клавиатура для возврата к выбору предмета куратора"""
    return InlineKeyboardMarkup(inline_keyboard=[
        get_universal_back_button(callback_data="back"),
        get_universal_back_button("🏠 Главное меню", "back_to_main")
    ])