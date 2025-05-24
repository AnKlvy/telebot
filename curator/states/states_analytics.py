from curator.handlers.analytics import AnalyticsStates
STATE_TRANSITIONS = {
    AnalyticsStates.select_group_for_student: AnalyticsStates.main,
    AnalyticsStates.select_student: AnalyticsStates.select_group_for_student,
    AnalyticsStates.student_stats: AnalyticsStates.select_student,
    AnalyticsStates.select_group_for_group: AnalyticsStates.main,
    AnalyticsStates.group_stats: AnalyticsStates.select_group_for_group,
    AnalyticsStates.main: None  # None означает возврат в главное меню
}

# Импортируем обработчики после определения класса состояний
from curator.handlers.analytics import (
    show_analytics_menu,
    select_group_for_student_analytics,
    select_student_for_analytics,
    show_student_analytics,
    select_group_for_group_analytics,
    show_group_analytics, AnalyticsStates
)

# Словарь обработчиков для каждого состояния
STATE_HANDLERS = {
    AnalyticsStates.main: show_analytics_menu,
    AnalyticsStates.select_group_for_student: select_group_for_student_analytics,
    AnalyticsStates.select_student: select_student_for_analytics,
    AnalyticsStates.student_stats: show_student_analytics,
    AnalyticsStates.select_group_for_group: select_group_for_group_analytics,
    AnalyticsStates.group_stats: show_group_analytics
}