from common.manager_tests.get_transitions_handlers import get_transitions_handlers
from manager.handlers.homework import (
    start_add_homework, select_subject, select_lesson, save_homework,
    select_homework_to_delete, show_homeworks_to_delete
)
from manager.handlers.homework import AddHomeworkStates
transitions, handlers = get_transitions_handlers(AddHomeworkStates, "manager")
# Словарь переходов между состояниями
STATE_TRANSITIONS = {
    AddHomeworkStates.main: AddHomeworkStates.select_course,
    AddHomeworkStates.select_subject: AddHomeworkStates.select_course,
    AddHomeworkStates.select_lesson: AddHomeworkStates.select_subject,
    **transitions,
    AddHomeworkStates.select_test_to_delete: AddHomeworkStates.delete_test
}

# Словарь обработчиков для каждого состояния
STATE_HANDLERS = {
    AddHomeworkStates.select_course: start_add_homework,
    AddHomeworkStates.select_subject: select_subject,
    AddHomeworkStates.select_lesson: select_lesson,
    **handlers,
    AddHomeworkStates.delete_test: select_homework_to_delete,
    AddHomeworkStates.select_test_to_delete: show_homeworks_to_delete
}