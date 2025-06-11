from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData
from common.keyboards import get_main_menu_back_button
from typing import List, Literal
from database import SubjectRepository

# Константы для действий с микротемами
class TopicActions:
    VIEW = "view"
    ADD = "add"
    DELETE = "del"
    CONFIRM_DELETE = "cdel"
    CANCEL = "cancel"

class TopicCallback(CallbackData, prefix="topic"):
    """Фабрика callback-данных для работы с микротемами"""
    action: Literal[TopicActions.VIEW, TopicActions.ADD, TopicActions.DELETE, 
                   TopicActions.CONFIRM_DELETE, TopicActions.CANCEL]  # Тип действия с микротемой
    subject: str  # Название предмета
    topic: str | None = None  # Название микротемы (опционально)

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
    """Клавиатура со списком микротем по предмету"""
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

    # Кнопка добавления новой микротемы
    if subject_id:
        keyboard.append([
            InlineKeyboardButton(
                text="➕ Добавить микротему",
                callback_data=TopicCallback(action=TopicActions.ADD, subject=str(subject_id)).pack()
            )
        ])

    # Список существующих микротем
    for microtopic in microtopics:
        keyboard.append([
            InlineKeyboardButton(
                text=f"📝 {microtopic.name}",
                callback_data=TopicCallback(action=TopicActions.VIEW, subject=str(microtopic.subject_id), topic=str(microtopic.id)).pack()
            ),
            InlineKeyboardButton(
                text="❌",
                callback_data=TopicCallback(action=TopicActions.DELETE, subject=str(microtopic.subject_id), topic=str(microtopic.id)).pack()
            )
        ])

    keyboard.extend(get_main_menu_back_button())
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def confirm_delete_topic_kb(subject: str, topic: str) -> InlineKeyboardMarkup:
    """Клавиатура подтверждения удаления микротемы"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Подтвердить", 
                callback_data=TopicCallback(action=TopicActions.CONFIRM_DELETE, subject=subject, topic=topic).pack()
            ),
            InlineKeyboardButton(
                text="❌ Отменить", 
                callback_data=TopicCallback(action=TopicActions.CANCEL, subject=subject).pack()
            )
        ],
        *get_main_menu_back_button()
    ]) 