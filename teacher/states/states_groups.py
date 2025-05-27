from teacher.handlers.groups import TeacherGroupStates, show_teacher_groups, show_teacher_students, show_teacher_student_profile

# Словарь переходов между состояниями
STATE_TRANSITIONS = {
    TeacherGroupStates.select_group: None,  # None означает возврат в главное меню преподавателя
    TeacherGroupStates.select_student: TeacherGroupStates.select_group,
    TeacherGroupStates.student_profile: TeacherGroupStates.select_student
}

# Словарь обработчиков для каждого состояния
STATE_HANDLERS = {
    TeacherGroupStates.select_group: show_teacher_groups,
    TeacherGroupStates.select_student: show_teacher_students,
    TeacherGroupStates.student_profile: show_teacher_student_profile
}