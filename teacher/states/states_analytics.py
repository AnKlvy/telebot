from teacher.handlers.analytics import TeacherAnalyticsStates, show_teacher_analytics_menu
from teacher.handlers.analytics import (
    teacher_select_group_for_student,
    teacher_select_student,
    teacher_show_student_stats,
    teacher_select_group_for_group,
    teacher_show_group_stats
)

# Словарь переходов между состояниями
STATE_TRANSITIONS = {
    TeacherAnalyticsStates.select_group_for_student: TeacherAnalyticsStates.main,
    TeacherAnalyticsStates.select_student: TeacherAnalyticsStates.select_group_for_student,
    TeacherAnalyticsStates.student_stats: TeacherAnalyticsStates.select_student,
    TeacherAnalyticsStates.select_group_for_group: TeacherAnalyticsStates.main,
    TeacherAnalyticsStates.group_stats: TeacherAnalyticsStates.select_group_for_group,
    TeacherAnalyticsStates.main: None  # None означает возврат в главное меню
}

# Словарь обработчиков для каждого состояния
STATE_HANDLERS = {
    TeacherAnalyticsStates.main: show_teacher_analytics_menu,
    TeacherAnalyticsStates.select_group_for_student: teacher_select_group_for_student,
    TeacherAnalyticsStates.select_student: teacher_select_student,
    TeacherAnalyticsStates.student_stats: teacher_show_student_stats,
    TeacherAnalyticsStates.select_group_for_group: teacher_select_group_for_group,
    TeacherAnalyticsStates.group_stats: teacher_show_group_stats
}