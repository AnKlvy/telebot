from common.student_tests.states import StudentTestsStates
from typing import Dict, Any, Callable
from common.student_tests.handlers import (
    handle_main,
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

    # Отдельные состояния результатов с логичными переходами
    StudentTestsStates.course_entry_result: StudentTestsStates.course_entry_subjects,  # К выбору предмета
    StudentTestsStates.month_entry_result: StudentTestsStates.month_entry_month_selected,  # К выбору месяца
    StudentTestsStates.month_control_result: StudentTestsStates.month_control_month_selected,  # К выбору месяца

    StudentTestsStates.main: None  # None означает возврат в главное меню студента
}

# Словарь обработчиков состояний
STATE_HANDLERS = {
    # Добавляем обработчик для главного меню тестов
    StudentTestsStates.main: handle_main,
    StudentTestsStates.test_in_progress: handle_test_in_progress,

    # Обработчики для отдельных состояний результатов
    StudentTestsStates.course_entry_result: handle_course_entry_subjects,
    StudentTestsStates.month_entry_result: handle_month_entry_month_selected,
    StudentTestsStates.month_control_result: handle_month_control_month_selected,

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