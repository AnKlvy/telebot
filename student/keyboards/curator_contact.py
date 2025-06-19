from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List
from common.keyboards import get_main_menu_back_button


async def get_curator_subjects_kb(subjects: List) -> InlineKeyboardMarkup:
    """Клавиатура выбора предмета для связи с куратором"""
    buttons = []

    # Сортируем предметы по имени для консистентности
    sorted_subjects = sorted(subjects, key=lambda s: s.name)

    for subject in sorted_subjects:
        buttons.append([
            InlineKeyboardButton(
                text=subject.name,
                callback_data=f"curator_{subject.id}"
            )
        ])

    buttons.extend(get_main_menu_back_button())
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_back_to_curator_kb() -> InlineKeyboardMarkup:
    """Клавиатура для возврата к выбору предмета куратора"""
    return InlineKeyboardMarkup(inline_keyboard=[
        *get_main_menu_back_button(),
    ])