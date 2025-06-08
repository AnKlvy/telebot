from manager.handlers.lessons import (
    show_courses,
    process_view_action,
    back_to_select_subject,
    back_to_lessons_list,
    start_add_lesson,
    confirm_delete,
    cancel_action,
    ManagerLessonStates
)

# Словарь переходов между состояниями
STATE_TRANSITIONS = {
    ManagerLessonStates.main: None,  # None означает возврат в главное меню менеджера
    ManagerLessonStates.select_subject: ManagerLessonStates.main,
    ManagerLessonStates.lessons_list: ManagerLessonStates.select_subject,
    ManagerLessonStates.adding_lesson: ManagerLessonStates.lessons_list,
    ManagerLessonStates.confirm_deletion: ManagerLessonStates.lessons_list,
}

# Словарь обработчиков для каждого состояния
STATE_HANDLERS = {
    ManagerLessonStates.main: show_courses,
    ManagerLessonStates.select_subject: back_to_select_subject,
    ManagerLessonStates.lessons_list: back_to_lessons_list,
    ManagerLessonStates.adding_lesson: start_add_lesson,
    ManagerLessonStates.confirm_deletion: confirm_delete,
}
