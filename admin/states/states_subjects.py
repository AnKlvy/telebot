from admin.handlers.subjects import AdminSubjectsStates
from admin.handlers.main import admin_subjects_menu, AdminMainStates

# Словарь переходов между состояниями
STATE_TRANSITIONS = {
    # Состояния добавления предмета
    AdminSubjectsStates.enter_subject_name: AdminMainStates.subjects_menu,  # Возврат в меню предметов
    AdminSubjectsStates.confirm_add_subject: AdminSubjectsStates.enter_subject_name,

    # Состояния удаления предмета
    AdminSubjectsStates.select_subject_to_delete: AdminMainStates.subjects_menu,  # Возврат в меню предметов
    AdminSubjectsStates.confirm_delete_subject: AdminSubjectsStates.select_subject_to_delete,
}

# Словарь обработчиков для каждого состояния
STATE_HANDLERS = {
    AdminSubjectsStates.enter_subject_name: admin_subjects_menu,
    AdminSubjectsStates.confirm_add_subject: admin_subjects_menu,
    AdminSubjectsStates.select_subject_to_delete: admin_subjects_menu,
    AdminSubjectsStates.confirm_delete_subject: admin_subjects_menu,
}
