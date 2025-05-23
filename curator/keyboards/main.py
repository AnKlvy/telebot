from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_curator_main_menu_kb() -> InlineKeyboardMarkup:
    """Клавиатура главного меню куратора"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👥 Мои группы", callback_data="curator_groups")],
        [InlineKeyboardButton(text="📨 Сообщения от учеников", callback_data="curator_messages")],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="curator_stats")]
    ])