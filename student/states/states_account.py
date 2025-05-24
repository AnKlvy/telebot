from student.handlers.account import AccountStates, show_account_info

# Словарь переходов между состояниями
STATE_TRANSITIONS = {
    AccountStates.main: None  # None означает возврат в главное меню
}

# Словарь обработчиков для каждого состояния
STATE_HANDLERS = {
    AccountStates.main: show_account_info
}