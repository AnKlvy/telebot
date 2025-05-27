from common.tests_statistics import show_tests_statistics_menu
from common.tests_statistics.states import TestsStatisticsStates
from teacher.handlers.tests import (
    TeacherTestsStatisticsStates,
    show_teacher_tests_statistics,
    teacher_show_course_entry_groups,
    teacher_show_month_entry_groups,
    teacher_show_month_entry_months,
    teacher_show_month_control_groups,
    teacher_show_month_control_months,
    teacher_show_ent_groups,
    teacher_show_ent_students, teacher_show_ent_statistics, teacher_show_course_entry_statistics,
    teacher_show_month_control_statistics, teacher_show_month_entry_statistics
)

# Словарь переходов между состояниями
STATE_TRANSITIONS = {
    TeacherTestsStatisticsStates.main: None,  # None означает возврат в главное меню
    
    # Переходы для входного теста курса
    TeacherTestsStatisticsStates.course_entry_select_group: TeacherTestsStatisticsStates.main,
    TeacherTestsStatisticsStates.course_entry_result: TeacherTestsStatisticsStates.course_entry_select_group,
    
    # Переходы для входного теста месяца
    TeacherTestsStatisticsStates.month_entry_select_group: TeacherTestsStatisticsStates.main,
    TeacherTestsStatisticsStates.month_entry_select_month: TeacherTestsStatisticsStates.month_entry_select_group,
    TeacherTestsStatisticsStates.month_entry_result: TeacherTestsStatisticsStates.month_entry_select_month,
    
    # Переходы для контрольного теста месяца
    TeacherTestsStatisticsStates.month_control_select_group: TeacherTestsStatisticsStates.main,
    TeacherTestsStatisticsStates.month_control_select_month: TeacherTestsStatisticsStates.month_control_select_group,
    TeacherTestsStatisticsStates.month_control_result: TeacherTestsStatisticsStates.month_control_select_month,
    
    # Переходы для пробного ЕНТ
    TeacherTestsStatisticsStates.ent_select_group: TeacherTestsStatisticsStates.main,
    TeacherTestsStatisticsStates.ent_select_student: TeacherTestsStatisticsStates.ent_select_group,
    TeacherTestsStatisticsStates.ent_result: TeacherTestsStatisticsStates.ent_select_student
}

# Словарь обработчиков для каждого состояния
STATE_HANDLERS = {
    TeacherTestsStatisticsStates.main: show_teacher_tests_statistics,
    
    # Обработчики для входного теста курса
    TeacherTestsStatisticsStates.course_entry_select_group: teacher_show_course_entry_groups,
    TeacherTestsStatisticsStates.course_entry_result: teacher_show_course_entry_statistics,
    
    # Обработчики для входного теста месяца
    TeacherTestsStatisticsStates.month_entry_select_group: teacher_show_month_entry_groups,
    TeacherTestsStatisticsStates.month_entry_select_month: teacher_show_month_entry_months,
    TeacherTestsStatisticsStates.month_entry_result: teacher_show_month_entry_statistics,
    
    # Обработчики для контрольного теста месяца
    TeacherTestsStatisticsStates.month_control_select_group: teacher_show_month_control_groups,
    TeacherTestsStatisticsStates.month_control_select_month: teacher_show_month_control_months,
    TeacherTestsStatisticsStates.month_control_result: teacher_show_month_control_statistics,
    
    # Обработчики для пробного ЕНТ
    TeacherTestsStatisticsStates.ent_select_group: teacher_show_ent_groups,
    TeacherTestsStatisticsStates.ent_select_student: teacher_show_ent_students,
    TeacherTestsStatisticsStates.ent_result: teacher_show_ent_statistics
}