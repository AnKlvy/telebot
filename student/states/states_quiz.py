from student.handlers.homework_quiz import confirm_test
from student.handlers.homework import choose_homework, HomeworkStates

# Словарь переходов между состояниями
STATE_TRANSITIONS = {
    HomeworkStates.test_in_progress: HomeworkStates.confirmation,
    HomeworkStates.confirmation: HomeworkStates.homework,  # Возврат к выбору домашних заданий
}

# Словарь обработчиков для каждого состояния
STATE_HANDLERS = {
    HomeworkStates.confirmation: confirm_test,  # Обработчик подтверждения квиза
    HomeworkStates.homework: choose_homework,  # При возврате из квиза идем к выбору ДЗ
}
