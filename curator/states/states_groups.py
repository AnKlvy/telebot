from curator.handlers.groups import CuratorGroupStates, show_curator_groups, show_group_students, show_student_profile

# Словарь переходов между состояниями
STATE_TRANSITIONS = {
    CuratorGroupStates.select_group: None,  # None означает возврат в главное меню куратора
    CuratorGroupStates.select_student: CuratorGroupStates.select_group,
    CuratorGroupStates.student_profile: CuratorGroupStates.select_student
}

# Словарь обработчиков для каждого состояния
STATE_HANDLERS = {
    CuratorGroupStates.select_group: show_curator_groups,
    CuratorGroupStates.select_student: show_group_students,
    CuratorGroupStates.student_profile: show_student_profile
}