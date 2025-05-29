from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData
from common.keyboards import get_main_menu_back_button
from typing import List, Literal

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

def get_subjects_kb() -> InlineKeyboardMarkup:
    """Клавиатура выбора предмета для микротемы"""
    subjects = ["Математика", "Русский язык", "Физика"]  # Здесь должен быть список предметов из БД
    keyboard = []
    
    for subject in subjects:
        keyboard.append([
            InlineKeyboardButton(
                text=subject,
                callback_data=TopicCallback(action=TopicActions.VIEW, subject=subject).pack()
            )
        ])
    
    keyboard.extend(get_main_menu_back_button())
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_topics_list_kb(subject: str, topics: List[str]) -> InlineKeyboardMarkup:
    """Клавиатура со списком микротем по предмету"""
    keyboard = []
    
    # Кнопка добавления новой микротемы
    keyboard.append([
        InlineKeyboardButton(
            text="➕ Добавить микротему",
            callback_data=TopicCallback(action=TopicActions.ADD, subject=subject).pack()
        )
    ])
    
    # Список существующих микротем
    for topic in topics:
        keyboard.append([
            InlineKeyboardButton(
                text=f"📝 {topic}",
                callback_data=TopicCallback(action=TopicActions.VIEW, subject=subject, topic=topic).pack()
            ),
            InlineKeyboardButton(
                text="❌",
                callback_data=TopicCallback(action=TopicActions.DELETE, subject=subject, topic=topic).pack()
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