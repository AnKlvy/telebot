from student.handlers.curator_contact import CuratorStates, show_curator_menu, show_curator_info

# Словарь переходов между состояниями
STATE_TRANSITIONS = {
    CuratorStates.curator_info: CuratorStates.main,
    CuratorStates.main: None  # None означает возврат в главное меню
}

# Словарь обработчиков для каждого состояния
STATE_HANDLERS = {
    CuratorStates.main: show_curator_menu,
    CuratorStates.curator_info: show_curator_info
}