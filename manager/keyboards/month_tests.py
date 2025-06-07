from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from common.keyboards import get_main_menu_back_button

def get_month_tests_menu_kb() -> InlineKeyboardMarkup:
    """Клавиатура главного меню тестов месяца"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Создать тест", callback_data="create_month_test")],
        [InlineKeyboardButton(text="📋 Список тестов", callback_data="list_month_tests")],
        [InlineKeyboardButton(text="🗑 Удалить тест", callback_data="delete_month_test")],
        *get_main_menu_back_button()
    ])

def get_courses_for_tests_kb() -> InlineKeyboardMarkup:
    """Клавиатура выбора курса для тестов"""
    courses = {
        1: "ЕНТ",
        2: "IT"
    }
    
    buttons = []
    for course_id, course_name in courses.items():
        buttons.append([
            InlineKeyboardButton(
                text=course_name,
                callback_data=f"course_{course_id}"
            )
        ])
    
    buttons.extend(get_main_menu_back_button())
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_subjects_for_tests_kb(course_id: int) -> InlineKeyboardMarkup:
    """Клавиатура выбора предмета для тестов"""
    subjects_db = {
        1: ["Математика", "Физика", "Информатика", "История Казахстана", "Химия", "Биология"],
        2: ["Python", "JavaScript", "Java"]
    }
    
    subjects = subjects_db.get(course_id, [])
    buttons = []
    
    for subject in subjects:
        buttons.append([
            InlineKeyboardButton(
                text=subject,
                callback_data=f"subject_{subject}"
            )
        ])
    
    buttons.extend(get_main_menu_back_button())
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_microtopics_input_kb() -> InlineKeyboardMarkup:
    """Клавиатура для ввода микротем"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back")]
    ])

def get_confirm_test_creation_kb() -> InlineKeyboardMarkup:
    """Клавиатура подтверждения создания теста"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Создать тест", callback_data="confirm_create_test")],
        [InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_create_test")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back")]
    ])

def get_tests_list_kb(tests_list: list) -> InlineKeyboardMarkup:
    """Клавиатура со списком созданных тестов"""
    buttons = []
    
    if not tests_list:
        buttons.append([
            InlineKeyboardButton(text="📝 Тестов пока нет", callback_data="no_tests")
        ])
    else:
        for test in tests_list:
            test_name = f"{test['course_name']} - {test['subject_name']} - {test['month_name']}"
            buttons.append([
                InlineKeyboardButton(
                    text=test_name,
                    callback_data=f"view_test_{test['id']}"
                )
            ])
    
    buttons.extend(get_main_menu_back_button())
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_confirm_delete_test_kb(test_id: str) -> InlineKeyboardMarkup:
    """Клавиатура подтверждения удаления теста"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🗑 Удалить", callback_data=f"confirm_delete_{test_id}")],
        [InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_delete")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back")]
    ])

def get_delete_tests_list_kb(tests_list: list) -> InlineKeyboardMarkup:
    """Клавиатура со списком тестов для удаления"""
    buttons = []
    
    if not tests_list:
        buttons.append([
            InlineKeyboardButton(text="📝 Тестов для удаления нет", callback_data="no_tests")
        ])
    else:
        for test in tests_list:
            test_name = f"{test['course_name']} - {test['subject_name']} - {test['month_name']}"
            buttons.append([
                InlineKeyboardButton(
                    text=f"🗑 {test_name}",
                    callback_data=f"delete_test_{test['id']}"
                )
            ])
    
    buttons.extend(get_main_menu_back_button())
    return InlineKeyboardMarkup(inline_keyboard=buttons)
