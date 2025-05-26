from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from .keyboards import get_tests_statistics_menu_kb
from .states import TestsStatisticsStates

async def show_tests_statistics_menu(callback: CallbackQuery, state: FSMContext, user_role: str = None):
    """
    Показать главное меню статистики тестов
    
    Args:
        callback: Объект CallbackQuery
        state: Контекст состояния FSM
        user_role: Роль пользователя (curator)
    """
    await callback.message.edit_text(
        "Выберите тип теста для просмотра статистики:",
        reply_markup=get_tests_statistics_menu_kb()
    )
    await state.set_state(TestsStatisticsStates.main)