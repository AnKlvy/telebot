from student.handlers.progress import ProgressStates, show_progress_menu, show_general_stats, show_subjects_list, show_subject_progress

# Словарь переходов между состояниями
STATE_TRANSITIONS = {
    ProgressStates.subject_details: ProgressStates.subjects,
    ProgressStates.subjects: ProgressStates.main,
    ProgressStates.common_stats: ProgressStates.main,
    ProgressStates.main: None  # None означает возврат в главное меню
}

# Словарь обработчиков для каждого состояния
STATE_HANDLERS = {
    ProgressStates.main: show_progress_menu,
    ProgressStates.common_stats: show_general_stats,
    ProgressStates.subjects: show_subjects_list,
    ProgressStates.subject_details: show_subject_progress
}