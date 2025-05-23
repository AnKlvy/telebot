from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_test_report_menu_kb() -> InlineKeyboardMarkup:
    """Клавиатура меню тест-отчета"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🟢 Входной тест курса", callback_data="course_entry_test")],
        [InlineKeyboardButton(text="📅 Входной тест месяца", callback_data="month_entry_test")],
        [InlineKeyboardButton(text="📅 Контрольный тест месяца", callback_data="month_control_test")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main")]
    ])

def get_test_subjects_kb(test_type: str) -> InlineKeyboardMarkup:
    """Клавиатура выбора предмета для теста"""
    buttons = [
        [InlineKeyboardButton(text="История Казахстана", callback_data=f"{test_type}_sub_kz")],
        [InlineKeyboardButton(text="Математическая грамотность", callback_data=f"{test_type}_sub_mathlit")],
        [InlineKeyboardButton(text="Математика", callback_data=f"{test_type}_sub_math")],
        [InlineKeyboardButton(text="География", callback_data=f"{test_type}_sub_geo")],
        [InlineKeyboardButton(text="Биология", callback_data=f"{test_type}_sub_bio")],
        [InlineKeyboardButton(text="Химия", callback_data=f"{test_type}_sub_chem")],
        [InlineKeyboardButton(text="Информатика", callback_data=f"{test_type}_sub_inf")],
        [InlineKeyboardButton(text="Всемирная история", callback_data=f"{test_type}_sub_world")],
        [InlineKeyboardButton(text="Грамотность чтения", callback_data=f"{test_type}_sub_read")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_test_report")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_month_test_kb(test_type: str, subject_id: str) -> InlineKeyboardMarkup:
    """Клавиатура выбора месяца для теста"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Месяц 1", callback_data=f"{test_type}_{subject_id}_month_1")],
        [InlineKeyboardButton(text="Месяц 2", callback_data=f"{test_type}_{subject_id}_month_2")],
        [InlineKeyboardButton(text="Месяц 3", callback_data=f"{test_type}_{subject_id}_month_3")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=f"back_to_{test_type}_subjects")]
    ])

def get_back_to_test_report_kb() -> InlineKeyboardMarkup:
    """Клавиатура для возврата в меню тест-отчета"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад к тестам", callback_data="back_to_test_report")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main")]
    ])