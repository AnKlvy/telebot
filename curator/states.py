from aiogram.fsm.state import State, StatesGroup

class CuratorHomeworkStates(StatesGroup):
    homework_menu = State()
    student_stats_course = State()
    student_stats_lesson = State()
    student_stats_list = State()
    group_stats_group = State()

# Словарь переходов между состояниями
STATE_TRANSITIONS = {
    CuratorHomeworkStates.student_stats_course: CuratorHomeworkStates.homework_menu,
    CuratorHomeworkStates.student_stats_lesson: CuratorHomeworkStates.student_stats_course,
    CuratorHomeworkStates.student_stats_list: CuratorHomeworkStates.student_stats_lesson,
    CuratorHomeworkStates.group_stats_group: CuratorHomeworkStates.homework_menu,
}

# Словарь обработчиков для каждого состояния
STATE_HANDLERS = {
    CuratorHomeworkStates.homework_menu: "show_homework_menu",
    CuratorHomeworkStates.student_stats_course: "select_student_stats_course",
    CuratorHomeworkStates.student_stats_lesson: "select_student_stats_lesson",
    CuratorHomeworkStates.student_stats_list: "show_student_stats_list",
    CuratorHomeworkStates.group_stats_group: "show_group_stats"
}
