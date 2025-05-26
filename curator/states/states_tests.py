from curator.handlers.tests import (
    CuratorTestsStatisticsStates,
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
    curator_back_to_tests_statistics
)

# Словарь обработчиков для каждого состояния
STATE_HANDLERS = {
    CuratorTestsStatisticsStates.main: show_curator_tests_statistics,
    CuratorTestsStatisticsStates.select_group: None,  # Обрабатывается через роутер
    CuratorTestsStatisticsStates.select_month: None,  # Обрабатывается через роутер
    CuratorTestsStatisticsStates.select_student: None,  # Обрабатывается через роутер
    CuratorTestsStatisticsStates.statistics_result: curator_back_to_tests_statistics
}

# Словарь переходов между состояниями
STATE_TRANSITIONS = {
    CuratorTestsStatisticsStates.main: None,  # None означает возврат в главное меню
    CuratorTestsStatisticsStates.select_group: CuratorTestsStatisticsStates.main,
    CuratorTestsStatisticsStates.select_month: CuratorTestsStatisticsStates.select_group,
    CuratorTestsStatisticsStates.select_student: CuratorTestsStatisticsStates.select_group,
    CuratorTestsStatisticsStates.statistics_result: CuratorTestsStatisticsStates.main
}