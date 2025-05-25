from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from .keyboards import get_tests_menu_kb
from .states import TestsStates

async def show_tests_menu(callback: CallbackQuery, state: FSMContext, user_role: str = None):
    """
    Показать главное меню тестов
    
    Args:
        callback: Объект CallbackQuery
        state: Контекст состояния FSM
        user_role: Роль пользователя (student, curator)
    """
    await callback.message.edit_text(
        "Выберите тип теста:",
        reply_markup=get_tests_menu_kb()
    )
    await state.set_state(TestsStates.main)