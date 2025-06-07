from manager.handlers.bonus_tasks import (
    show_bonus_task_management, start_add_bonus_task, process_task_name,
    process_task_description, process_price_selection, process_custom_price,
    save_bonus_task, edit_bonus_task, cancel_bonus_task,
    show_bonus_tasks_to_delete, confirm_delete_bonus_task, delete_bonus_task,
    cancel_delete_bonus_task, BonusTaskStates
)

# Словарь переходов между состояниями
STATE_TRANSITIONS = {
    BonusTaskStates.enter_task_name: BonusTaskStates.main,
    BonusTaskStates.enter_task_description: BonusTaskStates.enter_task_name,
    BonusTaskStates.enter_price: BonusTaskStates.enter_task_description,
    BonusTaskStates.confirm_task: BonusTaskStates.enter_price,
    BonusTaskStates.select_task_to_delete: BonusTaskStates.main,
    BonusTaskStates.delete_task: BonusTaskStates.select_task_to_delete,
    BonusTaskStates.main: None  # None означает возврат в главное меню
}

# Словарь обработчиков для каждого состояния
STATE_HANDLERS = {
    BonusTaskStates.main: show_bonus_task_management,
    BonusTaskStates.enter_task_name: process_task_name,
    BonusTaskStates.enter_task_description: process_task_description,
    BonusTaskStates.enter_price: process_price_selection,
    BonusTaskStates.confirm_task: save_bonus_task,
    BonusTaskStates.select_task_to_delete: show_bonus_tasks_to_delete,
    BonusTaskStates.delete_task: delete_bonus_task
}
