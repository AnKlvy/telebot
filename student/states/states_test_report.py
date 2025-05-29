from student.handlers.test_report import StudentTestStates, show_student_tests
from common.student_tests.handlers import (
    show_course_entry_subjects,
    show_month_entry_subjects,
    show_month_control_subjects
)

# Словарь переходов между состояниями
STATE_TRANSITIONS = {
    StudentTestStates.main: None,  # None означает возврат в главное меню студента
    StudentTestStates.select_group_entry: StudentTestStates.main,
    StudentTestStates.select_month_entry: StudentTestStates.select_group_entry,
    StudentTestStates.select_group_control: StudentTestStates.main,
    StudentTestStates.select_month_control: StudentTestStates.select_group_control,
    StudentTestStates.test_in_progress: None,  # При отмене теста возвращаемся в главное меню
    StudentTestStates.test_result: StudentTestStates.main
}

# Словарь обработчиков для каждого состояния
STATE_HANDLERS = {
    StudentTestStates.main: show_student_tests,
    StudentTestStates.select_group_entry: show_course_entry_subjects,  # Для входного теста курса
    StudentTestStates.select_month_entry: show_month_entry_subjects,   # Для входного теста месяца
    StudentTestStates.select_group_control: show_month_control_subjects, # Для контрольного теста месяца
    # Остальные обработчики вызываются через роутер в test_report.py
}