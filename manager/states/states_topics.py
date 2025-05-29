from manager.handlers.topics import (
    show_subjects,
    show_topics,
    start_add_topic,
    process_topic_name,
    confirm_delete,
    delete_topic,
    cancel_delete,
    ManagerTopicStates
)

# Словарь переходов между состояниями
STATE_TRANSITIONS = {
    ManagerTopicStates.main: None,  # None означает возврат в главное меню менеджера
    ManagerTopicStates.topics_list: ManagerTopicStates.main,
    ManagerTopicStates.adding_topic: ManagerTopicStates.topics_list,
    ManagerTopicStates.confirm_deletion: ManagerTopicStates.topics_list,
    ManagerTopicStates.process_topic_name: ManagerTopicStates.topics_list,
    ManagerTopicStates.delete_topic: ManagerTopicStates.topics_list,
    ManagerTopicStates.cancel_delete: ManagerTopicStates.topics_list
}

# Словарь обработчиков для каждого состояния
STATE_HANDLERS = {
    ManagerTopicStates.main: show_subjects,
    ManagerTopicStates.topics_list: show_topics,
    ManagerTopicStates.adding_topic: start_add_topic,
    ManagerTopicStates.confirm_deletion: confirm_delete,
    ManagerTopicStates.process_topic_name: process_topic_name,
    ManagerTopicStates.delete_topic: delete_topic,
    ManagerTopicStates.cancel_delete: cancel_delete,
    
}
