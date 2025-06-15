from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData
from common.keyboards import get_main_menu_back_button
from typing import List, Literal
from database import SubjectRepository

# Константы для действий с микротемами
class TopicActions:
    VIEW = "view"
    ADD = "add"
    DELETE_BY_NUMBER = "del_num"
    SHOW_LIST = "show_list"

class TopicCallback(CallbackData, prefix="topic"):
    """Фабрика callback-данных для работы с микротемами"""
    action: Literal[TopicActions.VIEW, TopicActions.ADD, TopicActions.DELETE_BY_NUMBER,
                   TopicActions.SHOW_LIST]  # Тип действия с микротемой
    subject: str  # ID предмета
    topic: str | None = None  # Дополнительные данные (опционально)

async def get_subjects_kb() -> InlineKeyboardMarkup:
    """Клавиатура выбора предмета для микротемы"""
    subjects = await SubjectRepository.get_all()
    keyboard = []

    for subject in subjects:
        keyboard.append([
            InlineKeyboardButton(
                text=subject.name,
                callback_data=TopicCallback(action=TopicActions.VIEW, subject=str(subject.id)).pack()
            )
        ])

    keyboard.extend(get_main_menu_back_button())
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

async def get_topics_list_kb(subject_name: str, microtopics: List) -> InlineKeyboardMarkup:
    """Клавиатура с основными действиями для микротем"""
    keyboard = []

    # Получаем subject_id из первой микротемы (если есть) или ищем по названию
    subject_id = None
    if microtopics:
        subject_id = microtopics[0].subject_id
    else:
        # Если микротем нет, ищем предмет по названию
        subjects = await SubjectRepository.get_all()
        for subject in subjects:
            if subject.name == subject_name:
                subject_id = subject.id
                break

    # Основные кнопки управления микротемами
    if subject_id:
        keyboard.extend([
            [InlineKeyboardButton(
                text="➕ Добавить микротемы",
                callback_data=TopicCallback(action=TopicActions.ADD, subject=str(subject_id)).pack()
            )],
            [InlineKeyboardButton(
                text="❌ Удалить микротему",
                callback_data=TopicCallback(action=TopicActions.DELETE_BY_NUMBER, subject=str(subject_id)).pack()
            )],
            [InlineKeyboardButton(
                text="📋 Список всех микротем",
                callback_data=TopicCallback(action=TopicActions.SHOW_LIST, subject=str(subject_id)).pack()
            )]
        ])

    keyboard.extend(get_main_menu_back_button())
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

