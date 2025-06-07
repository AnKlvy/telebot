from manager.handlers.month_tests import (
    show_month_tests_menu,
    start_create_test,
    select_course,
    select_subject,
    process_month_name,
    process_microtopics,
    confirm_create_test,
    cancel_create_test,
    list_month_tests,
    start_delete_test,
    confirm_delete_test,
    delete_test,
    cancel_delete,
    ManagerMonthTestsStates
)

# Словарь переходов между состояниями
STATE_TRANSITIONS = {
    ManagerMonthTestsStates.main: None,  # None означает возврат в главное меню менеджера
    ManagerMonthTestsStates.select_course: ManagerMonthTestsStates.main,
    ManagerMonthTestsStates.select_subject: ManagerMonthTestsStates.select_course,
    ManagerMonthTestsStates.enter_month_name: ManagerMonthTestsStates.select_subject,
    ManagerMonthTestsStates.enter_microtopics: ManagerMonthTestsStates.enter_month_name,
    ManagerMonthTestsStates.confirm_creation: ManagerMonthTestsStates.enter_microtopics,
    ManagerMonthTestsStates.tests_list: ManagerMonthTestsStates.main,
    ManagerMonthTestsStates.confirm_deletion: ManagerMonthTestsStates.main
}

# Словарь обработчиков для каждого состояния
STATE_HANDLERS = {
    ManagerMonthTestsStates.main: show_month_tests_menu,
    ManagerMonthTestsStates.select_course: start_create_test,
    ManagerMonthTestsStates.select_subject: select_course,
    ManagerMonthTestsStates.enter_month_name: select_subject,
    ManagerMonthTestsStates.enter_microtopics: process_month_name,
    ManagerMonthTestsStates.confirm_creation: process_microtopics,
    ManagerMonthTestsStates.tests_list: list_month_tests,
    ManagerMonthTestsStates.confirm_deletion: start_delete_test
}
