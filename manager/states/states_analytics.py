from manager.handlers.analytics import (
    ManagerAnalyticsStates,
    show_manager_analytics_menu,
    manager_select_curator_for_student,
    manager_select_group_for_student,
    manager_select_student_for_analytics,
    manager_show_student_analytics,
    manager_select_curator_for_group,
    manager_select_group_for_group,
    manager_show_group_analytics,
    manager_select_subject,
    manager_show_subject_analytics,
    manager_show_general_analytics
)

# Словарь переходов между состояниями
STATE_TRANSITIONS = {
    ManagerAnalyticsStates.main: None,  # None означает возврат в главное меню
    ManagerAnalyticsStates.select_curator_for_student: ManagerAnalyticsStates.main,
    ManagerAnalyticsStates.select_group_for_student: ManagerAnalyticsStates.select_curator_for_student,
    ManagerAnalyticsStates.select_student: ManagerAnalyticsStates.select_group_for_student,
    ManagerAnalyticsStates.student_stats: ManagerAnalyticsStates.select_student,
    ManagerAnalyticsStates.student_stats_display: ManagerAnalyticsStates.student_stats,  # Возврат к статистике студента
    ManagerAnalyticsStates.select_curator_for_group: ManagerAnalyticsStates.main,
    ManagerAnalyticsStates.select_group_for_group: ManagerAnalyticsStates.select_curator_for_group,
    ManagerAnalyticsStates.group_stats: ManagerAnalyticsStates.select_group_for_group,
    ManagerAnalyticsStates.group_stats_display: ManagerAnalyticsStates.group_stats,  # Возврат к статистике группы
    ManagerAnalyticsStates.select_subject: ManagerAnalyticsStates.main,
    ManagerAnalyticsStates.subject_stats: ManagerAnalyticsStates.select_subject,
    ManagerAnalyticsStates.subject_stats_display: ManagerAnalyticsStates.subject_stats,  # Возврат к статистике предмета
    ManagerAnalyticsStates.general_stats: ManagerAnalyticsStates.main
}

# Импорты для специальных обработчиков
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

# Специальные обработчики для менеджера, которые сохраняют данные о кураторе
async def manager_back_to_select_group_for_student(callback: CallbackQuery, state: FSMContext):
    """Возврат к выбору группы для статистики студента с сохранением куратора"""
    from common.analytics.handlers import select_group_for_student_analytics
    await select_group_for_student_analytics(callback, state, "manager")

async def manager_back_to_select_group_for_group(callback: CallbackQuery, state: FSMContext):
    """Возврат к выбору группы для статистики группы с сохранением куратора"""
    from common.analytics.handlers import select_group_for_group_analytics
    await select_group_for_group_analytics(callback, state, "manager")

# Словарь обработчиков для каждого состояния
STATE_HANDLERS = {
    ManagerAnalyticsStates.main: show_manager_analytics_menu,
    ManagerAnalyticsStates.select_curator_for_student: manager_select_curator_for_student,
    ManagerAnalyticsStates.select_group_for_student: manager_back_to_select_group_for_student,  # Специальный обработчик
    ManagerAnalyticsStates.select_student: manager_select_student_for_analytics,
    ManagerAnalyticsStates.student_stats: manager_show_student_analytics,
    ManagerAnalyticsStates.student_stats_display: manager_show_student_analytics,  # Тот же обработчик для отображения
    ManagerAnalyticsStates.select_curator_for_group: manager_select_curator_for_group,
    ManagerAnalyticsStates.select_group_for_group: manager_back_to_select_group_for_group,  # Специальный обработчик
    ManagerAnalyticsStates.group_stats: manager_show_group_analytics,
    ManagerAnalyticsStates.group_stats_display: manager_show_group_analytics,  # Тот же обработчик для отображения
    ManagerAnalyticsStates.select_subject: manager_select_subject,
    ManagerAnalyticsStates.subject_stats: manager_show_subject_analytics,
    ManagerAnalyticsStates.subject_stats_display: manager_show_subject_analytics,  # Тот же обработчик для отображения
    ManagerAnalyticsStates.general_stats: manager_show_general_analytics
}