from common.tests_statistics import show_tests_statistics_menu
from common.tests_statistics.states import TestsStatisticsStates
from curator.handlers.tests import (
    show_curator_tests_statistics,
    curator_show_course_entry_groups,
    curator_show_course_entry_statistics,
    curator_show_course_entry_student_statistics,
    curator_show_month_entry_groups,
    curator_show_month_entry_months,
    curator_show_month_entry_statistics,
    curator_show_month_entry_student_statistics,
    curator_show_month_control_groups,
    curator_show_month_control_months,
    curator_show_month_control_statistics,
    curator_show_month_control_student_statistics,
    curator_show_ent_groups,
    curator_show_ent_students,
    curator_show_ent_statistics,
)

# Словарь обработчиков для каждого состояния
STATE_HANDLERS = {
    TestsStatisticsStates.main: show_curator_tests_statistics,
    TestsStatisticsStates.select_group: show_tests_statistics_menu,  # Обрабатывается через роутер
    TestsStatisticsStates.select_month: show_tests_statistics_menu,  # Обрабатывается через роутер
    TestsStatisticsStates.select_student: show_tests_statistics_menu,  # Обрабатывается через роутер
    TestsStatisticsStates.statistics_result: show_tests_statistics_menu
}

# Словарь переходов между состояниями
STATE_TRANSITIONS = {
    TestsStatisticsStates.main: None,  # None означает возврат в главное меню
    TestsStatisticsStates.select_group: TestsStatisticsStates.main,
    TestsStatisticsStates.select_month: TestsStatisticsStates.main,
    TestsStatisticsStates.select_student: TestsStatisticsStates.main,
    TestsStatisticsStates.statistics_result: TestsStatisticsStates.main
}
