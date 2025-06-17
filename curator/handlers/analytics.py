from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from common.analytics.register_handlers import register_analytics_handlers

class CuratorAnalyticsStates(StatesGroup):
    main = State()
    select_group_for_student = State()
    select_student = State()
    student_stats = State()
    student_stats_display = State()  # Новое состояние для отображения статистики студента
    select_group_for_group = State()
    group_stats = State()
    group_stats_display = State()  # Новое состояние для отображения статистики группы
    select_subject = State()
    subject_stats = State()

router = Router()

# Регистрируем обработчики для куратора
register_analytics_handlers(router, CuratorAnalyticsStates, "curator")
