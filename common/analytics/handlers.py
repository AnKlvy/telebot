from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from .keyboards import (
    get_analytics_menu_kb, get_groups_for_analytics_kb, 
    get_students_for_analytics_kb
)
from common.statistics import (
    check_if_id_in_callback_data
)

async def show_analytics_menu(callback: CallbackQuery, state: FSMContext, role: str):
    """
    Базовый обработчик для показа меню аналитики
    
    Args:
        callback: Объект CallbackQuery
        state: Контекст состояния FSM
        role: Роль пользователя (curator)
    """
    await callback.message.edit_text(
        "Выберите тип аналитики:",
        reply_markup=get_analytics_menu_kb(role)
    )
    # Удаляем установку состояния

async def select_group_for_student_analytics(callback: CallbackQuery, state: FSMContext, role: str):
    """
    Базовый обработчик для выбора группы для статистики по ученику
    
    Args:
        callback: Объект CallbackQuery
        state: Контекст состояния FSM
        role: Роль пользователя (curator)
    """
    await callback.message.edit_text(
        "Выберите группу ученика:",
        reply_markup=get_groups_for_analytics_kb(role)
    )
    # Удаляем установку состояния

async def select_student_for_analytics(callback: CallbackQuery, state: FSMContext, role: str):
    """
    Базовый обработчик для выбора ученика для статистики
    
    Args:
        callback: Объект CallbackQuery
        state: Контекст состояния FSM
        role: Роль пользователя (curator)
    """
    group_id = await check_if_id_in_callback_data("analytics_group_", callback, state, "group")

    
    await callback.message.edit_text(
        "Выберите ученика для просмотра статистики:",
        reply_markup=get_students_for_analytics_kb(group_id)
    )
    # Удаляем установку состояния


async def select_group_for_group_analytics(callback: CallbackQuery, state: FSMContext, role: str):
    """
    Базовый обработчик для выбора группы для статистики по группе
    
    Args:
        callback: Объект CallbackQuery
        state: Контекст состояния FSM
        role: Роль пользователя (curator)
    """
    await callback.message.edit_text(
        "Выберите группу для просмотра статистики:",
        reply_markup=get_groups_for_analytics_kb(role)
    )
    # Удаляем установку состояния


