from student.handlers.trial_ent import (
    TrialEntStates, show_trial_ent_menu, choose_required_subjects,
    choose_profile_subjects, process_profile_subject, process_second_profile_subject,
    show_subjects, show_subject_analytics, back_to_trial_ent_results
)

# Словарь переходов между состояниями
STATE_TRANSITIONS = {
    TrialEntStates.required_subjects: TrialEntStates.main,
    TrialEntStates.profile_subjects: TrialEntStates.required_subjects,
    TrialEntStates.second_profile_subject: TrialEntStates.profile_subjects,
    TrialEntStates.test_in_progress: TrialEntStates.main,
    TrialEntStates.results: TrialEntStates.main,
    TrialEntStates.analytics_subjects: TrialEntStates.results,
    TrialEntStates.subject_analytics: TrialEntStates.analytics_subjects,
    TrialEntStates.confirming_end: TrialEntStates.test_in_progress,
    TrialEntStates.main: None  # None означает возврат в главное меню
}

# Словарь обработчиков для каждого состояния
STATE_HANDLERS = {
    TrialEntStates.main: show_trial_ent_menu,
    TrialEntStates.required_subjects: choose_required_subjects,
    TrialEntStates.profile_subjects: choose_profile_subjects,
    TrialEntStates.second_profile_subject: process_profile_subject,
    TrialEntStates.results: back_to_trial_ent_results,
    TrialEntStates.analytics_subjects: show_subjects,
    TrialEntStates.subject_analytics: show_subject_analytics
}