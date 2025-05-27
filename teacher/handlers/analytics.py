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
class TeacherAnalyticsStates(AnalyticsStates):
    pass

router = Router()

@router.callback_query(F.data == "teacher_analytics")
async def show_teacher_analytics_menu(callback: CallbackQuery, state: FSMContext):
    """Показать меню аналитики преподавателя"""
    await show_analytics_menu(callback, state, "teacher")

@router.callback_query(TeacherAnalyticsStates.main, F.data == "student_analytics")
async def teacher_select_group_for_student(callback: CallbackQuery, state: FSMContext):
    """Выбор группы для статистики по ученику"""
    await select_group_for_student_analytics(callback, state, "teacher")

@router.callback_query(TeacherAnalyticsStates.select_group_for_student, F.data.startswith("analytics_group_"))
async def teacher_select_student(callback: CallbackQuery, state: FSMContext):
    """Выбор ученика для статистики"""
    await select_student_for_analytics(callback, state, "teacher")

@router.callback_query(TeacherAnalyticsStates.select_student, F.data.startswith("analytics_student_"))
async def teacher_show_student_stats(callback: CallbackQuery, state: FSMContext):
    """Показать статистику по ученику"""
    await show_student_analytics(callback, state, "teacher")

@router.callback_query(TeacherAnalyticsStates.main, F.data == "group_analytics")
async def teacher_select_group_for_group(callback: CallbackQuery, state: FSMContext):
    """Выбор группы для статистики по группе"""
    await select_group_for_group_analytics(callback, state, "teacher")

@router.callback_query(TeacherAnalyticsStates.select_group_for_group, F.data.startswith("analytics_group_"))
async def teacher_show_group_stats(callback: CallbackQuery, state: FSMContext):
    """Показать статистику по группе"""
    await show_group_analytics(callback, state, "teacher")