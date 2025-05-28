from curator.handlers.tests import (
    CuratorTestsStatisticsStates,
    show_curator_tests_statistics,
    curator_show_course_entry_groups,
    curator_show_month_entry_groups,
    curator_show_month_entry_months,
    curator_show_month_control_groups,
    curator_show_month_control_months,
    curator_show_ent_groups,
    curator_show_ent_students
)

# Словарь переходов между состояниями
STATE_TRANSITIONS = {
    CuratorTestsStatisticsStates.main: None,  # None означает возврат в главное меню
    
    # Переходы для входного теста курса
    CuratorTestsStatisticsStates.course_entry_select_group: CuratorTestsStatisticsStates.main,
    CuratorTestsStatisticsStates.course_entry_result: CuratorTestsStatisticsStates.course_entry_select_group,
    
    # Переходы для входного теста месяца
    CuratorTestsStatisticsStates.month_entry_select_group: CuratorTestsStatisticsStates.main,
    CuratorTestsStatisticsStates.month_entry_select_month: CuratorTestsStatisticsStates.month_entry_select_group,
    CuratorTestsStatisticsStates.month_entry_result: CuratorTestsStatisticsStates.month_entry_select_month,
    
    # Переходы для контрольного теста месяца
    CuratorTestsStatisticsStates.month_control_select_group: CuratorTestsStatisticsStates.main,
    CuratorTestsStatisticsStates.month_control_select_month: CuratorTestsStatisticsStates.month_control_select_group,
    CuratorTestsStatisticsStates.month_control_result: CuratorTestsStatisticsStates.month_control_select_month,
    
    # Переходы для пробного ЕНТ
    CuratorTestsStatisticsStates.ent_select_group: CuratorTestsStatisticsStates.main,
    CuratorTestsStatisticsStates.ent_select_student: CuratorTestsStatisticsStates.ent_select_group,
    CuratorTestsStatisticsStates.ent_result: CuratorTestsStatisticsStates.ent_select_student
}

# Словарь обработчиков для каждого состояния
STATE_HANDLERS = {
    CuratorTestsStatisticsStates.main: show_curator_tests_statistics,
    
    # Обработчики для входного теста курса
    CuratorTestsStatisticsStates.course_entry_select_group: curator_show_course_entry_groups,
    CuratorTestsStatisticsStates.course_entry_result: curator_show_course_entry_groups,
    
    # Обработчики для входного теста месяца
    CuratorTestsStatisticsStates.month_entry_select_group: curator_show_month_entry_groups,
    CuratorTestsStatisticsStates.month_entry_select_month: curator_show_month_entry_months,
    CuratorTestsStatisticsStates.month_entry_result: curator_show_month_entry_months,
    
    # Обработчики для контрольного теста месяца
    CuratorTestsStatisticsStates.month_control_select_group: curator_show_month_control_groups,
    CuratorTestsStatisticsStates.month_control_select_month: curator_show_month_control_months,
    CuratorTestsStatisticsStates.month_control_result: curator_show_month_control_months,
    
    # Обработчики для пробного ЕНТ
    CuratorTestsStatisticsStates.ent_select_group: curator_show_ent_groups,
    CuratorTestsStatisticsStates.ent_select_student: curator_show_ent_students,
    CuratorTestsStatisticsStates.ent_result: curator_show_ent_students
}
