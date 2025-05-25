from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from common.analytics.states import AnalyticsStates
from common.analytics.handlers import (
    show_analytics_menu, select_group_for_student_analytics,
    select_student_for_analytics, show_student_analytics,
    select_group_for_group_analytics, show_group_analytics
)

# Используем базовые состояния
class CuratorAnalyticsStates(AnalyticsStates):
    pass

router = Router()

@router.callback_query(F.data == "curator_analytics")
async def show_curator_analytics_menu(callback: CallbackQuery, state: FSMContext):
    """Показать меню аналитики куратора"""
    await show_analytics_menu(callback, state, "curator")

@router.callback_query(CuratorAnalyticsStates.main, F.data == "student_analytics")
async def curator_select_group_for_student_analytics(callback: CallbackQuery, state: FSMContext):
    """Выбор группы для статистики по ученику"""
    await select_group_for_student_analytics(callback, state, "curator")

@router.callback_query(CuratorAnalyticsStates.select_group_for_student, F.data.startswith("analytics_group_"))
async def curator_select_student_for_analytics(callback: CallbackQuery, state: FSMContext):
    """Выбор ученика для статистики"""
    await select_student_for_analytics(callback, state, "curator")

@router.callback_query(CuratorAnalyticsStates.select_student, F.data.startswith("analytics_student_"))
async def curator_show_student_analytics(callback: CallbackQuery, state: FSMContext):
    """Показать статистику по ученику"""
    await show_student_analytics(callback, state, "curator")

@router.callback_query(CuratorAnalyticsStates.main, F.data == "group_analytics")
async def curator_select_group_for_group_analytics(callback: CallbackQuery, state: FSMContext):
    """Выбор группы для статистики по группе"""
    await select_group_for_group_analytics(callback, state, "curator")

@router.callback_query(CuratorAnalyticsStates.select_group_for_group, F.data.startswith("analytics_group_"))
async def curator_show_group_analytics(callback: CallbackQuery, state: FSMContext):
    """Показать статистику по группе"""
    await show_group_analytics(callback, state, "curator")

# Обработчик возврата к меню аналитики
@router.callback_query(F.data == "back_to_analytics")
async def back_to_analytics_menu(callback: CallbackQuery, state: FSMContext):
    """Вернуться в меню аналитики"""
    await show_curator_analytics_menu(callback, state)