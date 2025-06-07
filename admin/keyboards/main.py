from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_admin_main_menu_kb() -> InlineKeyboardMarkup:
    """Клавиатура главного меню админа"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📚 Добавить/убрать курс", callback_data="admin_courses")],
        [InlineKeyboardButton(text="📖 Добавить/убрать предметы", callback_data="admin_subjects")],
        [InlineKeyboardButton(text="👥 Добавить/убрать группу", callback_data="admin_groups")],
        [InlineKeyboardButton(text="🎓 Добавить/убрать ученика", callback_data="admin_students")],
        [InlineKeyboardButton(text="👨‍🏫 Добавить/убрать куратора", callback_data="admin_curators")],
        [InlineKeyboardButton(text="👩‍🏫 Добавить/убрать преподавателя", callback_data="admin_teachers")],
        [InlineKeyboardButton(text="👨‍💼 Добавить/убрать менеджера", callback_data="admin_managers")]
    ])

def get_admin_courses_menu_kb() -> InlineKeyboardMarkup:
    """Клавиатура меню управления курсами"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить курс", callback_data="add_course")],
        [InlineKeyboardButton(text="🗑 Убрать курс", callback_data="remove_course")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back")]
    ])

def get_admin_subjects_menu_kb() -> InlineKeyboardMarkup:
    """Клавиатура меню управления предметами"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить предмет", callback_data="add_subject")],
        [InlineKeyboardButton(text="🗑 Убрать предмет", callback_data="remove_subject")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back")]
    ])

def get_admin_groups_menu_kb() -> InlineKeyboardMarkup:
    """Клавиатура меню управления группами"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить группу", callback_data="add_group")],
        [InlineKeyboardButton(text="🗑 Убрать группу", callback_data="remove_group")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back")]
    ])

def get_admin_students_menu_kb() -> InlineKeyboardMarkup:
    """Клавиатура меню управления учениками"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить ученика", callback_data="add_student")],
        [InlineKeyboardButton(text="🗑 Убрать ученика", callback_data="remove_student")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back")]
    ])

def get_admin_curators_menu_kb() -> InlineKeyboardMarkup:
    """Клавиатура меню управления кураторами"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить куратора", callback_data="add_curator")],
        [InlineKeyboardButton(text="🗑 Убрать куратора", callback_data="remove_curator")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back")]
    ])

def get_admin_teachers_menu_kb() -> InlineKeyboardMarkup:
    """Клавиатура меню управления преподавателями"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить преподавателя", callback_data="add_teacher")],
        [InlineKeyboardButton(text="🗑 Убрать преподавателя", callback_data="remove_teacher")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back")]
    ])

def get_admin_managers_menu_kb() -> InlineKeyboardMarkup:
    """Клавиатура меню управления менеджерами"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить менеджера", callback_data="add_manager")],
        [InlineKeyboardButton(text="🗑 Убрать менеджера", callback_data="remove_manager")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back")]
    ])

def get_tariff_selection_kb() -> InlineKeyboardMarkup:
    """Клавиатура выбора тарифа для ученика"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📦 Стандарт", callback_data="tariff_standard")],
        [InlineKeyboardButton(text="⭐ Премиум", callback_data="tariff_premium")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back")]
    ])

def get_confirmation_kb(action: str, item_id: str = "") -> InlineKeyboardMarkup:
    """Клавиатура подтверждения действия"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"confirm_{action}_{item_id}")],
        [InlineKeyboardButton(text="❌ Отменить", callback_data=f"cancel_{action}")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back")]
    ])
