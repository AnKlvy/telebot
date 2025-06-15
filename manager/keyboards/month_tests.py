from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from common.keyboards import get_main_menu_back_button
from database.repositories.course_repository import CourseRepository
from database.repositories.subject_repository import SubjectRepository

def get_month_tests_menu_kb() -> InlineKeyboardMarkup:
    """Клавиатура главного меню тестов месяца"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Создать тест", callback_data="create_month_test")],
        [InlineKeyboardButton(text="📋 Список тестов", callback_data="list_month_tests")],
        [InlineKeyboardButton(text="🗑 Удалить тест", callback_data="delete_month_test")],
        *get_main_menu_back_button()
    ])

async def get_courses_for_tests_kb() -> InlineKeyboardMarkup:
    """Клавиатура выбора курса для тестов"""
    try:
        courses = await CourseRepository.get_all()
        buttons = []

        for course in courses:
            buttons.append([
                InlineKeyboardButton(
                    text=course.name,
                    callback_data=f"course_{course.id}"
                )
            ])

        buttons.extend(get_main_menu_back_button())
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    except Exception:
        # Fallback в случае ошибки
        buttons = [
            [InlineKeyboardButton(text="❌ Ошибка загрузки курсов", callback_data="error")]
        ]
        buttons.extend(get_main_menu_back_button())
        return InlineKeyboardMarkup(inline_keyboard=buttons)

async def get_subjects_for_tests_kb(course_id: int) -> InlineKeyboardMarkup:
    """Клавиатура выбора предмета для тестов"""
    try:
        subjects = await SubjectRepository.get_by_course(course_id)
        buttons = []

        for subject in subjects:
            buttons.append([
                InlineKeyboardButton(
                    text=subject.name,
                    callback_data=f"subject_{subject.id}"
                )
            ])

        buttons.extend(get_main_menu_back_button())
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    except Exception:
        # Fallback в случае ошибки
        buttons = [
            [InlineKeyboardButton(text="❌ Ошибка загрузки предметов", callback_data="error")]
        ]
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

async def get_delete_tests_list_kb(tests_list: list) -> InlineKeyboardMarkup:
    """Клавиатура со списком тестов для удаления"""
    buttons = []

    if not tests_list:
        buttons.append([
            InlineKeyboardButton(text="📝 Тестов для удаления нет", callback_data="no_tests")
        ])
    else:
        for test in tests_list:
            test_name = f"{test.course.name} - {test.subject.name} - {test.name}"
            buttons.append([
                InlineKeyboardButton(
                    text=f"🗑 {test_name}",
                    callback_data=f"delete_test_{test.id}"
                )
            ])

    buttons.extend(get_main_menu_back_button())
    return InlineKeyboardMarkup(inline_keyboard=buttons)
