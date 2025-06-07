from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from admin.utils.common import get_confirmation_kb, get_tariff_selection_kb
from common.keyboards import back_to_main_button


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

def get_admin_entity_menu_kb(entity_name: str, entity_name_accusative: str, callback_prefix: str) -> InlineKeyboardMarkup:
    """Универсальная клавиатура меню управления сущностями

    Args:
        entity_name: Название сущности в именительном падеже (курс, предмет, группа, ученик, куратор, преподаватель, менеджер)
        entity_name_accusative: Название сущности в винительном падеже (курс, предмет, группу, ученика, куратора, преподавателя, менеджера)
        callback_prefix: Префикс для callback_data (course, subject, group, student, curator, teacher, manager)
    """
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"➕ Добавить {entity_name_accusative}", callback_data=f"add_{callback_prefix}")],
        [InlineKeyboardButton(text=f"🗑 Убрать {entity_name_accusative}", callback_data=f"remove_{callback_prefix}")],
        back_to_main_button()
        ])



# Функции get_tariff_selection_kb и get_confirmation_kb теперь импортируются из admin.utils.common
