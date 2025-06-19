from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from common.keyboards import get_main_menu_back_button, get_universal_back_button


def get_tests_statistics_menu_kb() -> InlineKeyboardMarkup:
    """Клавиатура меню статистики тестов"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🟢 Входной тест курса", callback_data="stats_course_entry_test")],
        [InlineKeyboardButton(text="📅 Входной тест месяца", callback_data="stats_month_entry_test")],
        [InlineKeyboardButton(text="📅 Контрольный тест месяца", callback_data="stats_month_control_test")],
        [InlineKeyboardButton(text="🧪 Пробный ЕНТ", callback_data="stats_ent_test")],
        *get_main_menu_back_button()
            ])

def get_groups_kb(test_type: str) -> InlineKeyboardMarkup:
    """Клавиатура с группами для статистики тестов (старая версия для совместимости)"""
    # В реальном приложении группы будут загружаться из базы данных
    groups = [
        {"id": "geo_intensive", "name": "Интенсив. География"},
        {"id": "math_intensive", "name": "Интенсив. Математика"}
    ]

    buttons = []
    for group in groups:
        buttons.append([
            InlineKeyboardButton(
                text=group["name"],
                callback_data=f"{test_type}_group_{group['id']}"
            )
        ])

    # Добавляем кнопку "Назад"
    buttons.extend(get_main_menu_back_button())

    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def get_curator_groups_kb(test_type: str, groups: list) -> InlineKeyboardMarkup:
    """Клавиатура с группами куратора для статистики тестов"""
    buttons = []
    for group in groups:
        buttons.append([
            InlineKeyboardButton(
                text=f"{group.name} ({group.subject.name if group.subject else 'Без предмета'})",
                callback_data=f"{test_type}_group_{group.id}"
            )
        ])

    # Добавляем кнопку "Назад"
    buttons.extend(get_main_menu_back_button())

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_month_kb(test_type: str, group_id: str) -> InlineKeyboardMarkup:
    """Клавиатура с месяцами для статистики тестов"""
    months = [
        {"id": "1", "name": "1 месяц"},
        {"id": "2", "name": "2 месяц"},
        {"id": "3", "name": "3 месяц"},
        {"id": "4", "name": "4 месяц"},
        {"id": "5", "name": "5 месяц"},
        {"id": "6", "name": "6 месяц"},
        {"id": "7", "name": "7 месяц"},
        {"id": "8", "name": "8 месяц"},
        {"id": "9", "name": "9 месяц"}
    ]
    
    buttons = []
    for month in months:
        buttons.append([
            InlineKeyboardButton(
                text=month["name"],
                callback_data=f"{test_type}_month_{group_id}_{month['id']}"
            )
        ])
    
    # Добавляем кнопку "Назад"
    buttons.extend(get_main_menu_back_button())
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_students_kb(test_type: str, group_id: str, month_id: str = None) -> InlineKeyboardMarkup:
    """Клавиатура со студентами для статистики тестов"""
    # В реальном приложении студенты будут загружаться из базы данных
    students = [
        {"id": "student1", "name": "Мадияр Сапаров"},
        {"id": "student2", "name": "Артем Осипов"},
        {"id": "student3", "name": "Диана Нурланова"},
        {"id": "student4", "name": "Арман Сериков"}
    ]
    
    buttons = []
    for student in students:
        callback_data = f"{test_type}_student_{group_id}"
        if month_id:
            callback_data += f"_{month_id}"
        callback_data += f"_{student['id']}"
        
        buttons.append([
            InlineKeyboardButton(
                text=student["name"],
                callback_data=callback_data
            )
        ])
    
    # Добавляем кнопку "Назад"
    back_data = f"back_to_{test_type}_months_{group_id}" if month_id else f"back_to_{test_type}_groups"
    buttons.extend([
        [
        InlineKeyboardButton(
            text="◀️ Назад",
            callback_data=back_data
        )
    ],
    get_universal_back_button("🏠 Главное меню", "back_to_main")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_back_kb() -> InlineKeyboardMarkup:
    """Клавиатура для возврата в меню статистики тестов"""
    return InlineKeyboardMarkup(inline_keyboard=[
    *get_main_menu_back_button()
            ])