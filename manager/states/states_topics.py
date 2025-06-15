from manager.handlers.topics import (
    show_subjects,
    show_topics,
    start_add_topic,
    process_topic_name,
    start_delete_by_number,
    process_delete_number,
    show_microtopics_list,
    ManagerTopicStates
)

# Словарь переходов между состояниями
STATE_TRANSITIONS = {
    ManagerTopicStates.main: None,  # None означает возврат в главное меню менеджера
    ManagerTopicStates.topics_list: ManagerTopicStates.main,
    ManagerTopicStates.adding_topic: ManagerTopicStates.topics_list,
    ManagerTopicStates.delete_by_number: ManagerTopicStates.topics_list
}

# Словарь обработчиков для каждого состояния
STATE_HANDLERS = {
    ManagerTopicStates.main: show_subjects,
    ManagerTopicStates.topics_list: show_topics,
    ManagerTopicStates.adding_topic: start_add_topic,
    ManagerTopicStates.delete_by_number: start_delete_by_number
}
