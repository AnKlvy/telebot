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
    AdminMainStates.courses_menu: AdminMainStates.main,  # Возврат в главное меню админа
    AdminMainStates.subjects_menu: AdminMainStates.main,  # Возврат в главное меню админа
    AdminMainStates.groups_menu: AdminMainStates.main,  # Возврат в главное меню админа
    AdminMainStates.students_menu: AdminMainStates.main,  # Возврат в главное меню админа
    AdminMainStates.curators_menu: AdminMainStates.main,  # Возврат в главное меню админа
    AdminMainStates.teachers_menu: AdminMainStates.main,  # Возврат в главное меню админа
    AdminMainStates.managers_menu: AdminMainStates.main,  # Возврат в главное меню админа
}

# Словарь обработчиков для каждого состояния
STATE_HANDLERS = {
    AdminMainStates.main: admin_main_menu,
    AdminMainStates.courses_menu: admin_courses_menu,
    AdminMainStates.subjects_menu: admin_subjects_menu,
    AdminMainStates.groups_menu: admin_groups_menu,
    AdminMainStates.students_menu: admin_students_menu,
    AdminMainStates.curators_menu: admin_curators_menu,
    AdminMainStates.teachers_menu: admin_teachers_menu,
    AdminMainStates.managers_menu: admin_managers_menu,
}
