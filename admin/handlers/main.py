from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from admin.keyboards.main import (
    get_admin_main_menu_kb,
    get_admin_entity_menu_kb
)

router = Router()

class AdminMainStates(StatesGroup):
    main = State()  # Главное меню админа

async def show_admin_main_menu(message: Message):
    """Показать главное меню админа"""
    await message.answer(
        text="👑 Панель администратора\n\nВыберите действие:",
        reply_markup=get_admin_main_menu_kb()
    )

@router.callback_query(F.data == "admin_main")
async def admin_main_menu(callback: CallbackQuery, state: FSMContext):
    """Главное меню админа"""
    await state.set_state(AdminMainStates.main)
    await callback.message.edit_text(
        text="👑 Панель администратора\n\nВыберите действие:",
        reply_markup=get_admin_main_menu_kb()
    )

# Обработчики меню управления курсами
@router.callback_query(F.data == "admin_courses")
async def admin_courses_menu(callback: CallbackQuery, state: FSMContext):
    """Меню управления курсами"""
    await callback.message.edit_text(
        text="📚 Управление курсами\n\nВыберите действие:",
        reply_markup=get_admin_entity_menu_kb("курс", "курс", "course")
    )

# Обработчики меню управления предметами
@router.callback_query(F.data == "admin_subjects")
async def admin_subjects_menu(callback: CallbackQuery, state: FSMContext):
    """Меню управления предметами"""
    await callback.message.edit_text(
        text="📖 Управление предметами\n\nВыберите действие:",
        reply_markup=get_admin_entity_menu_kb("предмет", "предмет", "subject")
    )

# Обработчики меню управления группами
@router.callback_query(F.data == "admin_groups")
async def admin_groups_menu(callback: CallbackQuery, state: FSMContext):
    """Меню управления группами"""
    await callback.message.edit_text(
        text="👥 Управление группами\n\nВыберите действие:",
        reply_markup=get_admin_entity_menu_kb("группа", "группу", "group")
    )

# Обработчики меню управления учениками
@router.callback_query(F.data == "admin_students")
async def admin_students_menu(callback: CallbackQuery, state: FSMContext):
    """Меню управления учениками"""
    await callback.message.edit_text(
        text="🎓 Управление учениками\n\nВыберите действие:",
        reply_markup=get_admin_entity_menu_kb("ученик", "ученика", "student")
    )

# Обработчики меню управления кураторами
@router.callback_query(F.data == "admin_curators")
async def admin_curators_menu(callback: CallbackQuery, state: FSMContext):
    """Меню управления кураторами"""
    await callback.message.edit_text(
        text="👨‍🏫 Управление кураторами\n\nВыберите действие:",
        reply_markup=get_admin_entity_menu_kb("куратор", "куратора", "curator")
    )

# Обработчики меню управления преподавателями
@router.callback_query(F.data == "admin_teachers")
async def admin_teachers_menu(callback: CallbackQuery, state: FSMContext):
    """Меню управления преподавателями"""
    await callback.message.edit_text(
        text="👩‍🏫 Управление преподавателями\n\nВыберите действие:",
        reply_markup=get_admin_entity_menu_kb("преподаватель", "преподавателя", "teacher")
    )

# Обработчики меню управления менеджерами
@router.callback_query(F.data == "admin_managers")
async def admin_managers_menu(callback: CallbackQuery, state: FSMContext):
    """Меню управления менеджерами"""
    await callback.message.edit_text(
        text="👨‍💼 Управление менеджерами\n\nВыберите действие:",
        reply_markup=get_admin_entity_menu_kb("менеджер", "менеджера", "manager")
    )

# Заглушки для кнопок, которые еще не реализованы
@router.callback_query(F.data == "add_student")
async def add_student_placeholder(callback: CallbackQuery, state: FSMContext):
    """Заглушка для добавления ученика"""
    await callback.answer("🚧 Функция в разработке", show_alert=True)

@router.callback_query(F.data == "remove_student")
async def remove_student_placeholder(callback: CallbackQuery, state: FSMContext):
    """Заглушка для удаления ученика"""
    await callback.answer("🚧 Функция в разработке", show_alert=True)

# Кураторы и преподаватели теперь реализованы в staff.py
