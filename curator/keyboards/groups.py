from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_curator_groups_kb() -> InlineKeyboardMarkup:
    """Клавиатура выбора группы куратора"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📗 Химия — Премиум", callback_data="group_chem_premium")],
        [InlineKeyboardButton(text="📘 Биология — Интенсив", callback_data="group_bio_intensive")],
        [InlineKeyboardButton(text="📕 История — Базовый", callback_data="group_history_basic")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_curator_main")]
    ])

def get_group_students_kb(group_id: str) -> InlineKeyboardMarkup:
    """Клавиатура выбора ученика в группе"""
    # Упрощаем структуру - используем только ID студента в callback_data
    buttons = [
        [InlineKeyboardButton(text="👤 Аружан Ахметова", callback_data="student_1")],
        [InlineKeyboardButton(text="👤 Мадияр Сапаров", callback_data="student_2")],
        [InlineKeyboardButton(text="👤 Диана Ержанова", callback_data="student_3")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_groups")]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_student_profile_kb() -> InlineKeyboardMarkup:
    """Клавиатура для карточки ученика"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Посмотреть ДЗ", callback_data="view_student_homeworks")],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="view_student_stats")],
        [InlineKeyboardButton(text="📩 Написать сообщение", callback_data="message_to_student")],
        [InlineKeyboardButton(text="⬅️ Назад к списку", callback_data="back_to_students")]
    ])