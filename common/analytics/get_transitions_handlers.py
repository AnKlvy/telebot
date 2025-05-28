from common.analytics.handlers import (
    show_analytics_menu, select_group_for_student_analytics, select_student_for_analytics,
    select_group_for_group_analytics

)
from common.statistics import show_student_analytics, show_group_analytics


def get_transitions_handlers(states_group, role):
    """
    Creates dictionaries of transitions and handlers for student and curator analytics

    Args:
        states_group: State group (StudentAnalyticsStates or CuratorAnalyticsStates)
        role: User role ('student' or 'curator')

    Returns:
        tuple: (STATE_TRANSITIONS, STATE_HANDLERS) - dictionaries of transitions and handlers
    """
    # Словарь переходов между состояниями
    STATE_TRANSITIONS = {
        states_group.select_group_for_student: states_group.main,
        states_group.select_student: states_group.select_group_for_student,
        states_group.student_stats: states_group.select_student,
        states_group.select_group_for_group: states_group.main,
        states_group.group_stats: states_group.select_group_for_group,
        states_group.main: None  # None означает возврат в главное меню
    }

    # Словарь обработчиков для каждого состояния
    STATE_HANDLERS = {
        states_group.main: show_analytics_menu,
        states_group.select_group_for_student: select_group_for_student_analytics,
        states_group.select_student: select_student_for_analytics,
        states_group.student_stats: show_student_analytics,
        states_group.select_group_for_group: select_group_for_group_analytics,
        states_group.group_stats: show_group_analytics
    }

    return STATE_TRANSITIONS, STATE_HANDLERS