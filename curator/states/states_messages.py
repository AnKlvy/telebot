from curator.handlers.messages import MessageStates, show_messages_menu, select_group_for_individual, select_student_for_message, enter_individual_message, confirm_individual_message, select_group_for_mass, enter_mass_message, confirm_mass_message

# Словарь переходов между состояниями
STATE_TRANSITIONS = {
    MessageStates.main: None,  # None означает возврат в главное меню куратора
    # Переходы для индивидуальных сообщений
    MessageStates.select_group_individual: MessageStates.main,
    MessageStates.select_student: MessageStates.select_group_individual,
    MessageStates.enter_individual_message: MessageStates.select_student,
    MessageStates.confirm_individual_message: MessageStates.enter_individual_message,
    # Переходы для массовых сообщений
    MessageStates.select_group_mass: MessageStates.main,
    MessageStates.enter_mass_message: MessageStates.select_group_mass,
    MessageStates.confirm_mass_message: MessageStates.enter_mass_message
}

# Словарь обработчиков для каждого состояния
STATE_HANDLERS = {
    MessageStates.main: show_messages_menu,
    # Обработчики для индивидуальных сообщений
    MessageStates.select_group_individual: select_group_for_individual,
    MessageStates.select_student: select_student_for_message,
    MessageStates.enter_individual_message: enter_individual_message,
    MessageStates.confirm_individual_message: confirm_individual_message,
    # Обработчики для массовых сообщений
    MessageStates.select_group_mass: select_group_for_mass,
    MessageStates.enter_mass_message: enter_mass_message,
    MessageStates.confirm_mass_message: confirm_mass_message
}