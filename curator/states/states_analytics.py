from curator.handlers.analytics import CuratorAnalyticsStates
STATE_TRANSITIONS = {
    CuratorAnalyticsStates.select_group_for_student: CuratorAnalyticsStates.main,
    CuratorAnalyticsStates.select_student: CuratorAnalyticsStates.select_group_for_student,
    CuratorAnalyticsStates.student_stats: CuratorAnalyticsStates.select_student,
    CuratorAnalyticsStates.select_group_for_group: CuratorAnalyticsStates.main,
    CuratorAnalyticsStates.group_stats: CuratorAnalyticsStates.select_group_for_group,
    CuratorAnalyticsStates.main: None  # None означает возврат в главное меню
}

# Импортируем обработчики после определения класса состояний
from curator.handlers.analytics import (
    show_curator_analytics_menu,
    curator_select_group_for_student_analytics,
    curator_select_student_for_analytics,
    curator_show_student_analytics,
    curator_select_group_for_group_analytics,
    curator_show_group_analytics
)

# Словарь обработчиков для каждого состояния
STATE_HANDLERS = {
    CuratorAnalyticsStates.main: show_curator_analytics_menu,
    CuratorAnalyticsStates.select_group_for_student: curator_select_group_for_student_analytics,
    CuratorAnalyticsStates.select_student: curator_select_student_for_analytics,
    CuratorAnalyticsStates.student_stats: curator_show_student_analytics,
    CuratorAnalyticsStates.select_group_for_group: curator_select_group_for_group_analytics,
    CuratorAnalyticsStates.group_stats: curator_show_group_analytics
}