from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from common.keyboards import get_main_menu_back_button, get_universal_back_button, back_to_main_button


def get_photo_skip_kb() -> InlineKeyboardMarkup:
    """Клавиатура для пропуска добавления фото"""
    buttons = [[
        InlineKeyboardButton(
            text="⏩ Пропустить (без фото)",
            callback_data="skip_photo"
        )
    ], back_to_main_button()]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_correct_answer_kb() -> InlineKeyboardMarkup:
    """Клавиатура выбора правильного ответа"""
    buttons = []
    for letter in ["A", "B", "C", "D", "E"]:
        buttons.append([
            InlineKeyboardButton(
                text=f"Вариант {letter}", 
                callback_data=f"correct_{letter}"
            )
        ])

    buttons.append(back_to_main_button())
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_time_limit_kb() -> InlineKeyboardMarkup:
    """Клавиатура выбора времени на ответ"""
    time_options = [10, 20, 30, 60, 120, 180, 240, 300]
    
    buttons = []
    for time in time_options:
        text = f"{time} сек."
        if time >= 60:
            minutes = time // 60
            seconds = time % 60
            text = f"{minutes} мин."
            if seconds > 0:
                text += f" {seconds} сек."
        
        buttons.append([
            InlineKeyboardButton(
                text=text, 
                callback_data=f"time_{time}"
            )
        ])

    buttons.append(back_to_main_button())
    

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_add_question_kb(question_count: int) -> InlineKeyboardMarkup:
    """Клавиатура для добавления вопросов"""
    buttons = [[
        InlineKeyboardButton(
            text="➕ Добавить ещё вопрос",
            callback_data="add_more_question"
        )
    ], [
        InlineKeyboardButton(
            text=f"✅ Завершить ({question_count} вопросов)",
            callback_data="finish_adding_questions"
        )
    ], back_to_main_button()]

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_confirm_test_kb() -> InlineKeyboardMarkup:
    """Клавиатура подтверждения создания теста"""
    buttons = [
        [
            InlineKeyboardButton(
                text="✅ Подтвердить", 
                callback_data="confirm_test"
            )
        ],
        [
            InlineKeyboardButton(
                text="🔄 Изменить", 
                callback_data="edit_test"
            )
        ],
        [
            InlineKeyboardButton(
                text="❌ Отменить", 
                callback_data="cancel_test"
            )
        ],
        back_to_main_button()
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_tests_list_kb(tests: list) -> InlineKeyboardMarkup:
    """Клавиатура со списком тестов для удаления"""
    buttons = []
    for test in tests:
        buttons.append([
            InlineKeyboardButton(
                text=test["name"], 
                callback_data=f"delete_test_{test['id']}"
            )
        ])
    buttons.append(back_to_main_button())

    return InlineKeyboardMarkup(inline_keyboard=buttons) 