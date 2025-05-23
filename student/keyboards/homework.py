from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from common.keyboards import get_universal_back_button

def get_main_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Домашнее задание", callback_data="homework")],
        [InlineKeyboardButton(text="📊 Мой прогресс", callback_data="progress")],
        [InlineKeyboardButton(text="🎁 Магазин", callback_data="shop")],
        [InlineKeyboardButton(text="🧠 Тест-отчет", callback_data="test_report")],
        [InlineKeyboardButton(text="🧪 Пробный ЕНТ", callback_data="trial_ent")],
        [InlineKeyboardButton(text="📞 Связь с куратором", callback_data="curator")],
        [InlineKeyboardButton(text="❓ Аккаунт", callback_data="account")]
    ])

def get_courses_kb() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="Интенсив. География", callback_data="course_geo")],
        [InlineKeyboardButton(text="Интенсив. Математика", callback_data="course_math")],
        get_universal_back_button(callback_data="back")
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_subjects_kb() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="История Казахстана", callback_data="sub_kz")],
        [InlineKeyboardButton(text="Математическая грамотность", callback_data="sub_mathlit")],
        [InlineKeyboardButton(text="Математика", callback_data="sub_math")],
        [InlineKeyboardButton(text="География", callback_data="sub_geo")],
        [InlineKeyboardButton(text="Биология", callback_data="sub_bio")],
        [InlineKeyboardButton(text="Химия", callback_data="sub_chem")],
        [InlineKeyboardButton(text="Информатика", callback_data="sub_inf")],
        [InlineKeyboardButton(text="Всемирная история", callback_data="sub_world")],
        [InlineKeyboardButton(text="Грамотность чтения", callback_data="sub_read")],
        get_universal_back_button(callback_data="back")
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_lessons_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="1. Алканы", callback_data="lesson_alkanes")],
        [InlineKeyboardButton(text="2. Изомерия", callback_data="lesson_isomeria")],
        [InlineKeyboardButton(text="3. Кислоты", callback_data="lesson_acids")],
        get_universal_back_button(callback_data="back")
    ])

def get_homeworks_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Базовое", callback_data="homework_basic")],
        [InlineKeyboardButton(text="Углублённое", callback_data="homework_advanced")],
        [InlineKeyboardButton(text="Повторение", callback_data="homework_review")],
        get_universal_back_button(callback_data="back")
    ])

def get_confirm_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="▶️ Начать тест", callback_data="start_test")],
        get_universal_back_button(callback_data="back")
    ])

def get_test_answers_kb() -> InlineKeyboardMarkup:
    """Клавиатура с вариантами ответов на вопрос теста"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="A", callback_data="answer_A")],
        [InlineKeyboardButton(text="B", callback_data="answer_B")],
        [InlineKeyboardButton(text="C", callback_data="answer_C")],
        [InlineKeyboardButton(text="D", callback_data="answer_D")]
    ])

def get_after_test_kb() -> InlineKeyboardMarkup:
    """Клавиатура после завершения теста"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Пройти ещё раз", callback_data="retry_test")],
        [InlineKeyboardButton(text="📊 Мой прогресс", callback_data="progress")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main_menu")]
    ])

