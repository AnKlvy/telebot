from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from .keyboards import (
    get_analytics_menu_kb, get_groups_for_analytics_kb,
    get_students_for_analytics_kb, get_groups_by_curator_kb
)
from common.utils import check_if_id_in_callback_data


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
    # Получаем ID выбранного куратора из состояния
    data = await state.get_data()
    curator_id = data.get('selected_curator')

    if curator_id and role == "manager":
        # Если выбран куратор, показываем его группы
        keyboard = await get_groups_by_curator_kb(curator_id)
    else:
        # Иначе показываем все группы
        keyboard = await get_groups_for_analytics_kb(role)

    await callback.message.edit_text(
        "Выберите группу ученика:",
        reply_markup=keyboard
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

    
    students_kb = await get_students_for_analytics_kb(group_id)
    await callback.message.edit_text(
        "Выберите ученика для просмотра статистики:",
        reply_markup=students_kb
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
    groups_kb = await get_groups_for_analytics_kb(role)
    await callback.message.edit_text(
        "Выберите группу для просмотра статистики:",
        reply_markup=groups_kb
    )
    # Удаляем установку состояния


