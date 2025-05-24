# Импортируем обработчики после определения класса состояний
from curator.handlers.homeworks import (
    show_homework_menu,
    select_student_stats_course,
    select_student_stats_group,
    select_student_stats_subject,
    select_student_stats_lesson,
    show_student_stats_list,
    select_group_stats_group,
    show_group_stats,
    CuratorHomeworkStates
)

# Словарь переходов между состояниями
STATE_TRANSITIONS = {
    CuratorHomeworkStates.student_stats_course: CuratorHomeworkStates.homework_menu,
    CuratorHomeworkStates.student_stats_lesson: CuratorHomeworkStates.student_stats_course,
    CuratorHomeworkStates.student_stats_list: CuratorHomeworkStates.student_stats_lesson,
    CuratorHomeworkStates.group_stats_group: CuratorHomeworkStates.homework_menu,
    CuratorHomeworkStates.student_stats_group: CuratorHomeworkStates.student_stats_course,
    CuratorHomeworkStates.student_stats_subject: CuratorHomeworkStates.student_stats_group,
    CuratorHomeworkStates.group_stats_result: CuratorHomeworkStates.group_stats_group,
}

# Словарь обработчиков для каждого состояния
STATE_HANDLERS = {
    CuratorHomeworkStates.homework_menu: show_homework_menu,
    CuratorHomeworkStates.student_stats_course: select_student_stats_course,
    CuratorHomeworkStates.student_stats_group: select_student_stats_group,
    CuratorHomeworkStates.student_stats_subject: select_student_stats_subject,
    CuratorHomeworkStates.student_stats_lesson: select_student_stats_lesson,
    CuratorHomeworkStates.student_stats_list: show_student_stats_list,
    CuratorHomeworkStates.group_stats_group: select_group_stats_group,
    CuratorHomeworkStates.group_stats_result: show_group_stats
}
