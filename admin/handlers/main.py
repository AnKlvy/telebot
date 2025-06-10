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
    courses_menu = State()  # Меню управления курсами
    subjects_menu = State()  # Меню управления предметами
    groups_menu = State()  # Меню управления группами
    students_menu = State()  # Меню управления учениками
    curators_menu = State()  # Меню управления кураторами
    teachers_menu = State()  # Меню управления преподавателями
    managers_menu = State()  # Меню управления менеджерами

async def show_admin_main_menu(message: Message, state: FSMContext = None):
    """Показать главное меню админа"""
    if isinstance(message, Message):
        await message.answer(
            text="👑 Панель администратора\n\nВыберите действие:",
            reply_markup=get_admin_main_menu_kb()
        )
    else:  # CallbackQuery
        await message.message.edit_text(
            text="👑 Панель администратора\n\nВыберите действие:",
            reply_markup=get_admin_main_menu_kb()
        )

    if state:
        await state.set_state(AdminMainStates.main)

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
    await state.set_state(AdminMainStates.courses_menu)
    await callback.message.edit_text(
        text="📚 Управление курсами\n\nВыберите действие:",
        reply_markup=get_admin_entity_menu_kb("курс", "курс", "course")
    )

# Обработчики меню управления предметами
@router.callback_query(F.data == "admin_subjects")
async def admin_subjects_menu(callback: CallbackQuery, state: FSMContext):
    """Меню управления предметами"""
    await state.set_state(AdminMainStates.subjects_menu)
    await callback.message.edit_text(
        text="📖 Управление предметами\n\nВыберите действие:",
        reply_markup=get_admin_entity_menu_kb("предмет", "предмет", "subject")
    )

# Обработчики меню управления группами
@router.callback_query(F.data == "admin_groups")
async def admin_groups_menu(callback: CallbackQuery, state: FSMContext):
    """Меню управления группами"""
    await state.set_state(AdminMainStates.groups_menu)
    await callback.message.edit_text(
        text="👥 Управление группами\n\nВыберите действие:",
        reply_markup=get_admin_entity_menu_kb("группа", "группу", "group")
    )

# Обработчики меню управления учениками
@router.callback_query(F.data == "admin_students")
async def admin_students_menu(callback: CallbackQuery, state: FSMContext):
    """Меню управления учениками"""
    await state.set_state(AdminMainStates.students_menu)
    await callback.message.edit_text(
        text="🎓 Управление учениками\n\nВыберите действие:",
        reply_markup=get_admin_entity_menu_kb("ученик", "ученика", "student")
    )

# Обработчики меню управления кураторами
@router.callback_query(F.data == "admin_curators")
async def admin_curators_menu(callback: CallbackQuery, state: FSMContext):
    """Меню управления кураторами"""
    await state.set_state(AdminMainStates.curators_menu)
    await callback.message.edit_text(
        text="👨‍🏫 Управление кураторами\n\nВыберите действие:",
        reply_markup=get_admin_entity_menu_kb("куратор", "куратора", "curator")
    )

# Обработчики меню управления преподавателями
@router.callback_query(F.data == "admin_teachers")
async def admin_teachers_menu(callback: CallbackQuery, state: FSMContext):
    """Меню управления преподавателями"""
    await state.set_state(AdminMainStates.teachers_menu)
    await callback.message.edit_text(
        text="👩‍🏫 Управление преподавателями\n\nВыберите действие:",
        reply_markup=get_admin_entity_menu_kb("преподаватель", "преподавателя", "teacher")
    )

# Обработчики меню управления менеджерами
@router.callback_query(F.data == "admin_managers")
async def admin_managers_menu(callback: CallbackQuery, state: FSMContext):
    """Меню управления менеджерами"""
    await state.set_state(AdminMainStates.managers_menu)
    await callback.message.edit_text(
        text="👨‍💼 Управление менеджерами\n\nВыберите действие:",
        reply_markup=get_admin_entity_menu_kb("менеджер", "менеджера", "manager")
    )

# Все функции админ-панели реализованы!

# Кураторы и преподаватели теперь реализованы в staff.py
