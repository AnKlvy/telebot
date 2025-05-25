from aiogram.fsm.state import StatesGroup, State

class AnalyticsStates(StatesGroup):
    """Базовые состояния для аналитики"""
    main = State()
    select_group_for_student = State()
    select_student = State()
    student_stats = State()
    select_group_for_group = State()
    group_stats = State()