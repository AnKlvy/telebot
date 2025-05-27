from manager.handlers.homework import (
    start_add_homework, select_subject, select_lesson, enter_homework_name,
    start_adding_questions, add_question_photo, process_question_photo, skip_photo,
    select_topic, enter_answer_options, select_correct_answer, save_question,
    add_more_question, set_time_limit, confirm_homework, save_homework,
    edit_homework, cancel_homework, select_homework_to_delete, select_subject_for_delete,
    select_lesson_for_delete, show_homeworks_to_delete, confirm_delete_homework,
    delete_homework, cancel_delete_homework, back_to_homeworks,
    back_to_question_text, back_to_answer_options, back_to_questions, back_to_homework_name
)
from manager.handlers.homework import AddHomeworkStates

# Словарь переходов между состояниями
STATE_TRANSITIONS = {
    AddHomeworkStates.select_subject: AddHomeworkStates.select_course,
    AddHomeworkStates.select_lesson: AddHomeworkStates.select_subject,
    AddHomeworkStates.enter_homework_name: AddHomeworkStates.select_lesson,
    AddHomeworkStates.enter_question_text: AddHomeworkStates.enter_homework_name,
    AddHomeworkStates.add_question_photo: AddHomeworkStates.enter_question_text,
    AddHomeworkStates.select_topic: AddHomeworkStates.add_question_photo,
    AddHomeworkStates.enter_answer_options: AddHomeworkStates.select_topic,
    AddHomeworkStates.select_correct_answer: AddHomeworkStates.enter_answer_options,
    AddHomeworkStates.add_question: AddHomeworkStates.select_correct_answer,
    AddHomeworkStates.set_time_limit: AddHomeworkStates.add_question,
    AddHomeworkStates.confirm_homework: AddHomeworkStates.set_time_limit,
    AddHomeworkStates.select_homework_to_delete: AddHomeworkStates.delete_homework
}

# Словарь обработчиков для каждого состояния
STATE_HANDLERS = {
    AddHomeworkStates.select_course: start_add_homework,
    AddHomeworkStates.select_subject: select_subject,
    AddHomeworkStates.select_lesson: select_lesson,
    AddHomeworkStates.enter_homework_name: enter_homework_name,
    AddHomeworkStates.enter_question_text: start_adding_questions,
    AddHomeworkStates.add_question_photo: add_question_photo,
    AddHomeworkStates.select_topic: select_topic,
    AddHomeworkStates.enter_answer_options: enter_answer_options,
    AddHomeworkStates.select_correct_answer: select_correct_answer,
    AddHomeworkStates.add_question: save_question,
    AddHomeworkStates.set_time_limit: set_time_limit,
    AddHomeworkStates.confirm_homework: confirm_homework,
    AddHomeworkStates.delete_homework: select_homework_to_delete,
    AddHomeworkStates.select_homework_to_delete: show_homeworks_to_delete
}