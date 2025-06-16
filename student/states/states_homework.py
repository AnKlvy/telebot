from student.handlers.homework import HomeworkStates, choose_homework, choose_lesson, choose_subject, \
    choose_course
from student.handlers.homework_quiz import confirm_test, handle_test_back_navigation

# Словарь переходов между состояниями
STATE_TRANSITIONS = {
    HomeworkStates.confirmation: HomeworkStates.homework,
    HomeworkStates.homework: HomeworkStates.lesson,
    HomeworkStates.lesson: HomeworkStates.subject,
    HomeworkStates.subject: HomeworkStates.course,
    HomeworkStates.course: None,  # None означает возврат в главное меню
    HomeworkStates.test_in_progress: HomeworkStates.confirmation
}

# Словарь обработчиков для каждого состояния
STATE_HANDLERS = {
    HomeworkStates.course: choose_course,
    HomeworkStates.subject: choose_subject,
    HomeworkStates.lesson: choose_lesson,
    HomeworkStates.homework: choose_homework,
    HomeworkStates.confirmation: confirm_test,  # Обработчик подтверждения теста
    HomeworkStates.test_in_progress: handle_test_back_navigation,  # Специальный обработчик для возврата из теста
}
