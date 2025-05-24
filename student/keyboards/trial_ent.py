from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from common.keyboards import get_main_menu_back_button, get_universal_back_button


def get_trial_ent_start_kb() -> InlineKeyboardMarkup:
    """Клавиатура для начала пробного ЕНТ"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="▶️ Начать пробный ЕНТ", callback_data="start_trial_ent")],
        *get_main_menu_back_button()
    ])

def get_required_subjects_kb() -> InlineKeyboardMarkup:
    """Клавиатура выбора обязательных предметов"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="История Казахстана", callback_data="req_sub_kz")],
        [InlineKeyboardButton(text="Математическая грамотность", callback_data="req_sub_mathlit")],
        [InlineKeyboardButton(text="История Казахстана и Математическая грамотность", callback_data="req_sub_both")],
        *get_main_menu_back_button()
    ])

def get_profile_subjects_kb() -> InlineKeyboardMarkup:
    """Клавиатура выбора профильных предметов"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Математика", callback_data="prof_sub_math")],
        [InlineKeyboardButton(text="География", callback_data="prof_sub_geo")],
        [InlineKeyboardButton(text="Биология", callback_data="prof_sub_bio")],
        [InlineKeyboardButton(text="Химия", callback_data="prof_sub_chem")],
        [InlineKeyboardButton(text="Информатика", callback_data="prof_sub_inf")],
        [InlineKeyboardButton(text="Всемирная история", callback_data="prof_sub_world")],
        [InlineKeyboardButton(text="Нет профильных предметов", callback_data="prof_sub_none")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_required_subjects")]
    ])

def get_second_profile_subject_kb(first_subject: str) -> InlineKeyboardMarkup:
    """Клавиатура выбора второго профильного предмета"""
    buttons = []
    
    # Словарь соответствия callback_data и названий предметов
    subjects = {
        "prof_sub_math": "Математика",
        "prof_sub_geo": "География",
        "prof_sub_bio": "Биология",
        "prof_sub_chem": "Химия",
        "prof_sub_inf": "Информатика",
        "prof_sub_world": "Всемирная история"
    }
    
    # Добавляем все предметы, кроме уже выбранного
    for callback, name in subjects.items():
        if callback != first_subject:
            buttons.append([InlineKeyboardButton(text=name, callback_data=f"second_{callback}")])
    
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_profile_subjects")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_test_answers_kb() -> InlineKeyboardMarkup:
    """Клавиатура с вариантами ответов на вопрос теста"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="A", callback_data="answer_A")],
        [InlineKeyboardButton(text="B", callback_data="answer_B")],
        [InlineKeyboardButton(text="C", callback_data="answer_C")],
        [InlineKeyboardButton(text="D", callback_data="answer_D")],
        # Пустая строка для визуального разделения
        [InlineKeyboardButton(text="➖➖➖➖➖➖➖➖", callback_data="separator")],
        [InlineKeyboardButton(text="❌ Завершить тест", callback_data="end_trial_ent")]
    ])

def get_after_trial_ent_kb() -> InlineKeyboardMarkup:
    """Клавиатура после завершения пробного ЕНТ"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Посмотреть аналитику", callback_data="view_analytics")],
        [InlineKeyboardButton(text="🔄 Пройти ещё раз", callback_data="retry_trial_ent")],
        *get_main_menu_back_button()
    ])

def get_analytics_subjects_kb(subjects: list) -> InlineKeyboardMarkup:
    """Клавиатура выбора предмета для просмотра аналитики"""
    buttons = []
    
    for subject in subjects:
        if subject == "kz":
            buttons.append([InlineKeyboardButton(text="История Казахстана", callback_data="analytics_kz")])
        elif subject == "mathlit":
            buttons.append([InlineKeyboardButton(text="Математическая грамотность", callback_data="analytics_mathlit")])
        elif subject == "math":
            buttons.append([InlineKeyboardButton(text="Математика", callback_data="analytics_math")])
        elif subject == "geo":
            buttons.append([InlineKeyboardButton(text="География", callback_data="analytics_geo")])
        elif subject == "bio":
            buttons.append([InlineKeyboardButton(text="Биология", callback_data="analytics_bio")])
        elif subject == "chem":
            buttons.append([InlineKeyboardButton(text="Химия", callback_data="analytics_chem")])
        elif subject == "inf":
            buttons.append([InlineKeyboardButton(text="Информатика", callback_data="analytics_inf")])
        elif subject == "world":
            buttons.append([InlineKeyboardButton(text="Всемирная история", callback_data="analytics_world")])
    
    buttons.append(*get_main_menu_back_button())
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_back_to_analytics_kb() -> InlineKeyboardMarkup:
    """Клавиатура для возврата к выбору предмета для аналитики"""
    return InlineKeyboardMarkup(inline_keyboard=[
        get_universal_back_button("⬅️ Назад к выбору предмета", "back_to_analytics_subjects"),
        get_universal_back_button("🏠 Главное меню", "back_to_main")
    ])