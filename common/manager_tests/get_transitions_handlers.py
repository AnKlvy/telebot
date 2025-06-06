from .handlers import (
    enter_test_name, process_question_photo,
    set_time_limit,
    start_adding_questions, add_question_photo, skip_photo, enter_answer_options, select_correct_answer,
    save_question, confirm_test
)

def get_transitions_handlers(states_group, role):
    """
    Создает словари переходов и обработчиков для тестов менеджера

    Args:
        states_group: Группа состояний
        role: Роль пользователя

    Returns:
        tuple: (STATE_TRANSITIONS, STATE_HANDLERS) - словари переходов и обработчиков
    """
    # Словарь переходов между состояниями
    STATE_TRANSITIONS = {
        states_group.enter_test_name: states_group.select_lesson,
        states_group.enter_question_text: states_group.enter_test_name,
        states_group.add_question_photo: states_group.enter_question_text,
        states_group.skip_photo: states_group.add_question_photo,
        states_group.enter_answer_options: states_group.process_topic,
        states_group.select_correct_answer: states_group.enter_answer_options,
        states_group.add_question: states_group.select_correct_answer,
        states_group.set_time_limit: states_group.add_question,
        states_group.confirm_test: states_group.set_time_limit,
        states_group.main: None
    }

    # Словарь обработчиков для каждого состояния
    STATE_HANDLERS = {
        states_group.enter_test_name: enter_test_name,
        states_group.enter_question_text: start_adding_questions,
        states_group.add_question_photo: add_question_photo,
        states_group.process_photo: process_question_photo,
        states_group.skip_photo: skip_photo,
        states_group.enter_answer_options: enter_answer_options,
        states_group.select_correct_answer: select_correct_answer,
        states_group.add_question: save_question,
        states_group.set_time_limit: set_time_limit,
        states_group.confirm_test: confirm_test,
    }

    return STATE_TRANSITIONS, STATE_HANDLERS 