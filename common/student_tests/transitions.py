from common.student_tests.states import StudentTestsStates
from typing import Dict, Any, Callable
from common.student_tests.handlers import (
    handle_main,
    handle_test_result,
    handle_test_in_progress,
    handle_select_group_entry,
    handle_select_month_entry,
    handle_select_group_control,
    handle_select_month_control
)

# Словарь переходов между состояниями
STATE_TRANSITIONS = {
    StudentTestsStates.select_group_entry: StudentTestsStates.main,
    StudentTestsStates.select_month_entry: StudentTestsStates.main,
    StudentTestsStates.select_group_control: StudentTestsStates.main,
    StudentTestsStates.select_month_control: StudentTestsStates.select_group_control,
    StudentTestsStates.test_in_progress: StudentTestsStates.main,
    StudentTestsStates.test_result: StudentTestsStates.main,
    StudentTestsStates.main: None  # None означает возврат в главное меню
}

# Словарь обработчиков состояний
STATE_HANDLERS = {
    None: handle_main,  # Обработчик главного меню
    StudentTestsStates.main: handle_main,
    StudentTestsStates.test_result: handle_test_result,
    StudentTestsStates.test_in_progress: handle_test_in_progress,
    StudentTestsStates.select_group_entry: handle_select_group_entry,
    StudentTestsStates.select_month_entry: handle_select_month_entry,
    StudentTestsStates.select_group_control: handle_select_group_control,
    StudentTestsStates.select_month_control: handle_select_month_control
} 