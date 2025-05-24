from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from ..keyboards.analytics import (
    get_analytics_menu_kb, get_groups_for_analytics_kb, 
    get_students_for_analytics_kb, get_back_to_analytics_kb
)
from common.statistics import (
    get_student_topics_stats, get_group_stats,
    format_student_topics_stats, format_group_stats
)
from aiogram.fsm.state import State, StatesGroup

class AnalyticsStates(StatesGroup):
    main = State()
    select_group_for_student = State()
    select_student = State()
    student_stats = State()
    select_group_for_group = State()
    group_stats = State()


router = Router()

@router.callback_query(F.data == "curator_analytics")
async def show_analytics_menu(callback: CallbackQuery, state: FSMContext):
    """Показать меню аналитики"""
    await callback.message.edit_text(
        "Выберите тип аналитики:",
        reply_markup=get_analytics_menu_kb()
    )
    await state.set_state(AnalyticsStates.main)

# Обработчики для статистики по ученику
@router.callback_query(AnalyticsStates.main, F.data == "student_analytics")
async def select_group_for_student_analytics(callback: CallbackQuery, state: FSMContext):
    """Выбор группы для статистики по ученику"""
    await callback.message.edit_text(
        "Выберите группу ученика:",
        reply_markup=get_groups_for_analytics_kb()
    )
    await state.set_state(AnalyticsStates.select_group_for_student)

@router.callback_query(AnalyticsStates.select_group_for_student, F.data.startswith("analytics_group_"))
async def select_student_for_analytics(callback: CallbackQuery, state: FSMContext):
    """Выбор ученика для статистики"""
    group_id = callback.data.replace("analytics_group_", "")
    await state.update_data(selected_group=group_id)
    
    await callback.message.edit_text(
        "Выберите ученика для просмотра статистики:",
        reply_markup=get_students_for_analytics_kb(group_id)
    )
    await state.set_state(AnalyticsStates.select_student)

@router.callback_query(AnalyticsStates.select_student, F.data.startswith("analytics_student_"))
async def show_student_analytics(callback: CallbackQuery, state: FSMContext):
    """Показать статистику по ученику"""
    student_id = callback.data.replace("analytics_student_", "")
    
    # Получаем данные о студенте из общего компонента
    student_data = get_student_topics_stats(student_id)
    
    # Форматируем статистику в текст
    result_text = format_student_topics_stats(student_data)
    
    await callback.message.edit_text(
        result_text,
        reply_markup=get_back_to_analytics_kb()
    )
    await state.set_state(AnalyticsStates.student_stats)

# Обработчики для статистики по группе
@router.callback_query(AnalyticsStates.main, F.data == "group_analytics")
async def select_group_for_group_analytics(callback: CallbackQuery, state: FSMContext):
    """Выбор группы для статистики по группе"""
    await callback.message.edit_text(
        "Выберите группу для просмотра статистики:",
        reply_markup=get_groups_for_analytics_kb()
    )
    await state.set_state(AnalyticsStates.select_group_for_group)

@router.callback_query(AnalyticsStates.select_group_for_group, F.data.startswith("analytics_group_"))
async def show_group_analytics(callback: CallbackQuery, state: FSMContext):
    """Показать статистику по группе"""
    group_id = callback.data.replace("analytics_group_", "")
    
    # Получаем данные о группе из общего компонента
    group_data = get_group_stats(group_id)
    
    # Форматируем статистику в текст
    result_text = format_group_stats(group_data)
    
    await callback.message.edit_text(
        result_text,
        reply_markup=get_back_to_analytics_kb()
    )
    await state.set_state(AnalyticsStates.group_stats)