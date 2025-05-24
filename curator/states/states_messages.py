from curator.handlers.messages import MessageStates, show_messages_menu, select_group_for_individual, select_student_for_message, enter_individual_message, confirm_individual_message, select_group_for_mass, enter_mass_message, confirm_mass_message

# Словарь переходов между состояниями
STATE_TRANSITIONS = {
    MessageStates.main: None,  # None означает возврат в главное меню куратора
    MessageStates.select_group: MessageStates.main,
    MessageStates.select_student: MessageStates.select_group,
    MessageStates.enter_individual_message: MessageStates.select_student,
    MessageStates.confirm_individual_message: MessageStates.enter_individual_message,
    MessageStates.enter_mass_message: MessageStates.select_group,
    MessageStates.confirm_mass_message: MessageStates.enter_mass_message
}

# Словарь обработчиков для каждого состояния
STATE_HANDLERS = {
    MessageStates.main: show_messages_menu,
    MessageStates.select_group: select_group_for_individual,
    MessageStates.select_student: select_student_for_message,
    MessageStates.enter_individual_message: enter_individual_message,
    MessageStates.confirm_individual_message: confirm_individual_message,
    MessageStates.enter_mass_message: enter_mass_message,
    MessageStates.confirm_mass_message: confirm_mass_message
}