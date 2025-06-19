import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

router = Router()

# Импортируем менеджер навигации
from common.register_handlers_and_transitions import navigation_manager

async def log(name, role, state):
    logging.info(f"ВЫЗОВ: {name} | РОЛЬ: {role} | СОСТОЯНИЕ: {await state.get_state()}")

@router.callback_query(F.data == "back")
async def go_back(callback: CallbackQuery, state: FSMContext, user_role: str = None):
    await log("go_back", user_role, state)
    await navigation_manager.handle_back(callback, state, user_role)

# Регистрация обработчика кнопки "Главное меню"
@router.callback_query(F.data == "back_to_main")
async def back_to_main_handler(callback: CallbackQuery, state: FSMContext, user_role: str):
    await log("back_to_main_handler", user_role, state)
    await navigation_manager.handle_main_menu(callback, state, user_role)

# Обработчики кнопок постоянной клавиатуры
@router.message(F.text == "ученик")
async def keyboard_student_handler(message: Message, state: FSMContext, user_role: str = None):
    """Обработчик кнопки 'ученик' с клавиатуры"""
    await log("keyboard_student_handler", user_role, state)
    from student.handlers.main import show_student_main_menu
    await show_student_main_menu(message, user_role=user_role)

@router.message(F.text == "админ")
async def keyboard_admin_handler(message: Message, state: FSMContext, user_role: str = None):
    """Обработчик кнопки 'админ' с клавиатуры"""
    await log("keyboard_admin_handler", user_role, state)
    if user_role == "admin":
        from admin.handlers.main import show_admin_main_menu
        await show_admin_main_menu(message, user_role=user_role)

@router.message(F.text == "менеджер")
async def keyboard_manager_handler(message: Message, state: FSMContext, user_role: str = None):
    """Обработчик кнопки 'менеджер' с клавиатуры"""
    await log("keyboard_manager_handler", user_role, state)
    if user_role in ["admin", "manager"]:
        from manager.handlers.main import show_manager_main_menu
        await show_manager_main_menu(message, user_role=user_role)

@router.message(F.text == "преподаватель")
async def keyboard_teacher_handler(message: Message, state: FSMContext, user_role: str = None):
    """Обработчик кнопки 'преподаватель' с клавиатуры"""
    await log("keyboard_teacher_handler", user_role, state)
    if user_role in ["admin", "teacher"]:
        from teacher.handlers.main import show_teacher_main_menu
        await show_teacher_main_menu(message, user_role=user_role)

@router.message(F.text == "куратор")
async def keyboard_curator_handler(message: Message, state: FSMContext, user_role: str = None):
    """Обработчик кнопки 'куратор' с клавиатуры"""
    await log("keyboard_curator_handler", user_role, state)
    if user_role in ["admin", "curator"]:
        from curator.handlers.main import show_curator_main_menu
        await show_curator_main_menu(message, user_role=user_role)

@router.message(F.text == "старт")
async def keyboard_start_handler(message: Message, state: FSMContext, user_role: str = None):
    """Обработчик кнопки 'старт' с клавиатуры"""
    await log("keyboard_start_handler", user_role, state)
    # Перенаправляем на команду /start
    if user_role == "admin":
        from admin.handlers.main import show_admin_main_menu
        await show_admin_main_menu(message, user_role=user_role)
    elif user_role == "manager":
        from manager.handlers.main import show_manager_main_menu
        await show_manager_main_menu(message, user_role=user_role)
    elif user_role == "curator":
        from curator.handlers.main import show_curator_main_menu
        await show_curator_main_menu(message, user_role=user_role)
    elif user_role == "teacher":
        from teacher.handlers.main import show_teacher_main_menu
        await show_teacher_main_menu(message, user_role=user_role)
    else:  # По умолчанию считаем пользователя студентом
        from student.handlers.main import show_student_main_menu
        await show_student_main_menu(message, user_role=user_role)
