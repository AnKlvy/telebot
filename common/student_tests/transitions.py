from common.student_tests.states import StudentTestsStates
from typing import Dict, Any, Callable
from common.student_tests.handlers import (
    handle_main,
    handle_test_result,
    handle_test_in_progress,
    handle_course_entry_subjects,
    handle_course_entry_subject_selected,
    handle_course_entry_confirmation,
    handle_month_entry_subjects,
    handle_month_entry_subject_selected,
    handle_month_entry_month_selected,
    handle_month_entry_confirmation,
    handle_month_control_subjects,
    handle_month_control_subject_selected,
    handle_month_control_month_selected,
    handle_month_control_confirmation
)

# Словарь переходов между состояниями
STATE_TRANSITIONS = {
    # Входной тест курса
    StudentTestsStates.course_entry_subjects: StudentTestsStates.main,
    StudentTestsStates.course_entry_subject_selected: StudentTestsStates.course_entry_subjects,
    StudentTestsStates.course_entry_confirmation: StudentTestsStates.course_entry_subject_selected,

    # Входной тест месяца
    StudentTestsStates.month_entry_subjects: StudentTestsStates.main,
    StudentTestsStates.month_entry_subject_selected: StudentTestsStates.month_entry_subjects,
    StudentTestsStates.month_entry_month_selected: StudentTestsStates.month_entry_subject_selected,
    StudentTestsStates.month_entry_confirmation: StudentTestsStates.month_entry_month_selected,

    # Контрольный тест месяца
    StudentTestsStates.month_control_subjects: StudentTestsStates.main,
    StudentTestsStates.month_control_subject_selected: StudentTestsStates.month_control_subjects,
    StudentTestsStates.month_control_month_selected: StudentTestsStates.month_control_subject_selected,
    StudentTestsStates.month_control_confirmation: StudentTestsStates.month_control_month_selected,

    # Общие состояния
    StudentTestsStates.test_in_progress: StudentTestsStates.main,  # Из теста возвращаемся в главное меню
    StudentTestsStates.test_result: StudentTestsStates.main,
    StudentTestsStates.main: None  # None означает возврат в главное меню студента
}

# Словарь обработчиков состояний
STATE_HANDLERS = {
    # Убираем StudentTestsStates.main: handle_main - из главного меню тестов "Назад" должен вести в главное меню студента
    StudentTestsStates.test_result: handle_test_result,
    StudentTestsStates.test_in_progress: handle_test_in_progress,

    # Входной тест курса
    StudentTestsStates.course_entry_subjects: handle_course_entry_subjects,
    StudentTestsStates.course_entry_subject_selected: handle_course_entry_subject_selected,
    StudentTestsStates.course_entry_confirmation: handle_course_entry_confirmation,

    # Входной тест месяца
    StudentTestsStates.month_entry_subjects: handle_month_entry_subjects,
    StudentTestsStates.month_entry_subject_selected: handle_month_entry_subject_selected,
    StudentTestsStates.month_entry_month_selected: handle_month_entry_month_selected,
    StudentTestsStates.month_entry_confirmation: handle_month_entry_confirmation,

    # Контрольный тест месяца
    StudentTestsStates.month_control_subjects: handle_month_control_subjects,
    StudentTestsStates.month_control_subject_selected: handle_month_control_subject_selected,
    StudentTestsStates.month_control_month_selected: handle_month_control_month_selected,
    StudentTestsStates.month_control_confirmation: handle_month_control_confirmation
}