from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from common.keyboards import get_main_menu_back_button, get_universal_back_button


def get_homework_management_kb() -> InlineKeyboardMarkup:
    """Клавиатура управления домашними заданиями"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить ДЗ", callback_data="manager_add_homework")],
        [InlineKeyboardButton(text="❌ Удалить ДЗ", callback_data="manager_delete_homework")],
        *get_main_menu_back_button()
    ])

def get_courses_kb() -> InlineKeyboardMarkup:
    """Клавиатура выбора курса"""
    # В реальном приложении здесь будет запрос к базе данных
    courses = [
        {"id": "course_geo", "name": "Интенсив. География"},
        {"id": "course_math", "name": "Интенсив. Математика"}
    ]
    
    buttons = []
    for course in courses:
        buttons.append([
            InlineKeyboardButton(
                text=course["name"], 
                callback_data=course["id"]
            )
        ])
    
    buttons.extend(get_main_menu_back_button())
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_subjects_kb(course_id: str = None) -> InlineKeyboardMarkup:
    """Клавиатура выбора предмета"""
    # В реальном приложении здесь будет запрос к базе данных
    subjects = [
        {"id": "sub_kz", "name": "История Казахстана"},
        {"id": "sub_mathlit", "name": "Математическая грамотность"},
        {"id": "sub_math", "name": "Математика"},
        {"id": "sub_geo", "name": "География"},
        {"id": "sub_bio", "name": "Биология"},
        {"id": "sub_chem", "name": "Химия"},
        {"id": "sub_inf", "name": "Информатика"}
    ]
    
    buttons = []
    for subject in subjects:
        buttons.append([
            InlineKeyboardButton(
                text=subject["name"], 
                callback_data=subject["id"]
            )
        ])
    
    buttons.extend(get_main_menu_back_button())
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_lessons_kb(subject_id: str = None) -> InlineKeyboardMarkup:
    """Клавиатура выбора урока"""
    # В реальном приложении здесь будет запрос к базе данных
    lessons = [
        {"id": "lesson_alkanes", "name": "1. Алканы"},
        {"id": "lesson_isomeria", "name": "2. Изомерия"},
        {"id": "lesson_acids", "name": "3. Кислоты"}
    ]
    
    buttons = []
    for lesson in lessons:
        buttons.append([
            InlineKeyboardButton(
                text=lesson["name"], 
                callback_data=lesson["id"]
            )
        ])
    
    buttons.append([
        InlineKeyboardButton(
            text="➕ Добавить новый урок", 
            callback_data="add_new_lesson"
        )
    ])
    
    buttons.extend(get_main_menu_back_button())
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_topics_kb(lesson_id: str = None) -> InlineKeyboardMarkup:
    """Клавиатура выбора микротемы"""
    # В реальном приложении здесь будет запрос к базе данных
    topics = [
        {"id": "topic_1", "name": "Строение алканов"},
        {"id": "topic_2", "name": "Номенклатура алканов"},
        {"id": "topic_3", "name": "Физические свойства алканов"},
        {"id": "topic_4", "name": "Химические свойства алканов"}
    ]
    
    buttons = []
    for topic in topics:
        buttons.append([
            InlineKeyboardButton(
                text=topic["name"], 
                callback_data=f"topic_{topic['id']}"
            )
        ])
    
    buttons.append([
        InlineKeyboardButton(
            text="➕ Добавить новую микротему", 
            callback_data="add_new_topic"
        )
    ])
    
    buttons.extend(get_main_menu_back_button())
    
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
    
    buttons.extend(get_main_menu_back_button())
    
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
    
    buttons.extend(get_main_menu_back_button())
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_add_question_kb(question_count: int) -> InlineKeyboardMarkup:
    """Клавиатура для добавления вопросов"""
    buttons = [
        [
            InlineKeyboardButton(
                text="➕ Добавить ещё вопрос", 
                callback_data="add_more_question"
            )
        ],
        [
            InlineKeyboardButton(
                text=f"✅ Завершить ({question_count} вопросов)", 
                callback_data="finish_adding_questions"
            )
        ],
        *get_main_menu_back_button()
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_confirm_homework_kb() -> InlineKeyboardMarkup:
    """Клавиатура подтверждения создания ДЗ"""
    buttons = [
        [
            InlineKeyboardButton(
                text="✅ Подтвердить", 
                callback_data="confirm_homework"
            )
        ],
        [
            InlineKeyboardButton(
                text="🔄 Изменить", 
                callback_data="edit_homework"
            )
        ],
        [
            InlineKeyboardButton(
                text="❌ Отменить", 
                callback_data="cancel_homework"
            )
        ],
        *get_main_menu_back_button()
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_homeworks_list_kb(lesson_id: str) -> InlineKeyboardMarkup:
    """Клавиатура со списком ДЗ для удаления"""
    # В реальном приложении здесь будет запрос к базе данных
    homeworks = [
        {"id": "hw_1", "name": "Базовое ДЗ по алканам"},
        {"id": "hw_2", "name": "Углубленное ДЗ по алканам"},
        {"id": "hw_3", "name": "ДЗ на повторение"}
    ]
    
    buttons = []
    for hw in homeworks:
        buttons.append([
            InlineKeyboardButton(
                text=hw["name"], 
                callback_data=f"delete_hw_{hw['id']}"
            )
        ])
    
    buttons.extend(get_main_menu_back_button())
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_photo_skip_kb() -> InlineKeyboardMarkup:
    """Клавиатура для пропуска добавления фото"""
    buttons = [
        [
            InlineKeyboardButton(
                text="⏩ Пропустить (без фото)", 
                callback_data="skip_photo"
            )
        ],
        *get_main_menu_back_button()
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)