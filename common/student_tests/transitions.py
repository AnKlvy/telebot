from common.student_tests.states import StudentTestsStates
from typing import Dict, Any, Callable
from common.student_tests.handlers import (
    handle_main,
    handle_test_result,
    handle_test_in_progress,
    handle_course_entry_subjects,
    handle_course_entry_subject_selected,
    handle_month_entry_subjects,
    handle_month_entry_subject_selected,
    handle_month_entry_month_selected,
    handle_month_control_subjects,
    handle_month_control_subject_selected,
    handle_month_control_month_selected
)

# Словарь переходов между состояниями
STATE_TRANSITIONS = {
    # Входной тест курса
    StudentTestsStates.course_entry_subjects: StudentTestsStates.main,
    StudentTestsStates.course_entry_subject_selected: StudentTestsStates.course_entry_subjects,

    # Входной тест месяца
    StudentTestsStates.month_entry_subjects: StudentTestsStates.main,
    StudentTestsStates.month_entry_subject_selected: StudentTestsStates.month_entry_subjects,
    StudentTestsStates.month_entry_month_selected: StudentTestsStates.month_entry_subject_selected,

    # Контрольный тест месяца
    StudentTestsStates.month_control_subjects: StudentTestsStates.main,
    StudentTestsStates.month_control_subject_selected: StudentTestsStates.month_control_subjects,
    StudentTestsStates.month_control_month_selected: StudentTestsStates.month_control_subject_selected,

    # Общие состояния
    StudentTestsStates.test_in_progress: StudentTestsStates.main,
    StudentTestsStates.test_result: StudentTestsStates.main,
    StudentTestsStates.main: None  # None означает возврат в главное меню студента
}

# Словарь обработчиков состояний
STATE_HANDLERS = {
    None: handle_main,  # Обработчик главного меню
    StudentTestsStates.main: handle_main,
    StudentTestsStates.test_result: handle_test_result,
    StudentTestsStates.test_in_progress: handle_test_in_progress,

    # Входной тест курса
    StudentTestsStates.course_entry_subjects: handle_course_entry_subjects,
    StudentTestsStates.course_entry_subject_selected: handle_course_entry_subject_selected,

    # Входной тест месяца
    StudentTestsStates.month_entry_subjects: handle_month_entry_subjects,
    StudentTestsStates.month_entry_subject_selected: handle_month_entry_subject_selected,
    StudentTestsStates.month_entry_month_selected: handle_month_entry_month_selected,

    # Контрольный тест месяца
    StudentTestsStates.month_control_subjects: handle_month_control_subjects,
    StudentTestsStates.month_control_subject_selected: handle_month_control_subject_selected,
    StudentTestsStates.month_control_month_selected: handle_month_control_month_selected
}