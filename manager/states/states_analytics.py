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
    ManagerAnalyticsStates.select_curator_for_group: ManagerAnalyticsStates.main,
    ManagerAnalyticsStates.select_group_for_group: ManagerAnalyticsStates.select_curator_for_group,
    ManagerAnalyticsStates.group_stats: ManagerAnalyticsStates.select_group_for_group,
    ManagerAnalyticsStates.select_subject: ManagerAnalyticsStates.main,
    ManagerAnalyticsStates.subject_stats: ManagerAnalyticsStates.select_subject,
    ManagerAnalyticsStates.general_stats: ManagerAnalyticsStates.main
}

# Словарь обработчиков для каждого состояния
STATE_HANDLERS = {
    ManagerAnalyticsStates.main: show_manager_analytics_menu,
    ManagerAnalyticsStates.select_curator_for_student: manager_select_curator_for_student,
    ManagerAnalyticsStates.select_group_for_student: manager_select_group_for_student,
    ManagerAnalyticsStates.select_student: manager_select_student_for_analytics,
    ManagerAnalyticsStates.student_stats: manager_show_student_analytics,
    ManagerAnalyticsStates.select_curator_for_group: manager_select_curator_for_group,
    ManagerAnalyticsStates.select_group_for_group: manager_select_group_for_group,
    ManagerAnalyticsStates.group_stats: manager_show_group_analytics,
    ManagerAnalyticsStates.select_subject: manager_select_subject,
    ManagerAnalyticsStates.subject_stats: manager_show_subject_analytics,
    ManagerAnalyticsStates.general_stats: manager_show_general_analytics
}