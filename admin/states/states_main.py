from admin.handlers.main import (
    show_admin_main_menu,
    admin_main_menu,
    admin_courses_menu,
    admin_subjects_menu,
    admin_groups_menu,
    admin_students_menu,
    admin_curators_menu,
    admin_teachers_menu,
    admin_managers_menu,
    AdminMainStates
)

# Словарь переходов между состояниями
STATE_TRANSITIONS = {
    AdminMainStates.main: None,  # None означает возврат в главное меню админа
}

# Словарь обработчиков для каждого состояния
STATE_HANDLERS = {
    AdminMainStates.main: admin_main_menu,
}
