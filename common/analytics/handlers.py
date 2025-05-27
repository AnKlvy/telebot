from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from .states import AnalyticsStates
from .keyboards import (
    get_analytics_menu_kb, get_groups_for_analytics_kb, 
    get_students_for_analytics_kb, get_back_to_analytics_kb
)
from common.statistics import (
    get_student_topics_stats, get_group_stats,
    format_student_topics_stats, format_group_stats
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
    # Проверяем, является ли callback.data ID группы или это кнопка "назад"
    if callback.data.startswith("analytics_group_"):
        group_id = callback.data.replace("analytics_group_", "")
        print("group_id: ", group_id)
        await state.update_data(selected_group=group_id)
    else:
        # Если это кнопка "назад" или другой callback, берем ID группы из состояния
        user_data = await state.get_data()
        group_id = user_data.get("selected_group")
        print("Using saved group_id: ", group_id)
    
    await callback.message.edit_text(
        "Выберите ученика для просмотра статистики:",
        reply_markup=get_students_for_analytics_kb(group_id)
    )
    # Удаляем установку состояния

async def show_student_analytics(callback: CallbackQuery, state: FSMContext, role: str):
    """
    Базовый обработчик для показа статистики по ученику
    
    Args:
        callback: Объект CallbackQuery
        state: Контекст состояния FSM
        role: Роль пользователя (curator)
    """
    student_id = callback.data.replace("analytics_student_", "")
    
    # Получаем данные о студенте из общего компонента
    student_data = get_student_topics_stats(student_id)
    
    # Форматируем статистику в текст
    result_text = format_student_topics_stats(student_data)
    
    await callback.message.edit_text(
        result_text,
        reply_markup=get_back_to_analytics_kb()
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

async def show_group_analytics(callback: CallbackQuery, state: FSMContext, role: str):
    """
    Базовый обработчик для показа статистики по группе
    
    Args:
        callback: Объект CallbackQuery
        state: Контекст состояния FSM
        role: Роль пользователя (curator)
    """
    group_id = callback.data.replace("analytics_group_", "")
    
    # Получаем данные о группе из общего компонента
    group_data = get_group_stats(group_id)
    
    # Форматируем статистику в текст
    result_text = format_group_stats(group_data)
    
    await callback.message.edit_text(
        result_text,
        reply_markup=get_back_to_analytics_kb()
    )
    # Удаляем установку состояния
