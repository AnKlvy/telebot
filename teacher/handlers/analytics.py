from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from common.analytics.register_handlers import register_analytics_handlers


# Используем базовые состояния
class TeacherAnalyticsStates(StatesGroup):
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
    subject_stats_display = State()  # Новое состояние для отображения статистики предмета

router = Router()

register_analytics_handlers(router, TeacherAnalyticsStates, 'teacher')