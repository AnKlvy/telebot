from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from admin.utils.common import managers_db, add_person, remove_person
from admin.utils.handlers_generator import generate_person_entity_handlers

router = Router()

class AdminManagersStates(StatesGroup):
    # Состояния для добавления менеджера
    enter_manager_name = State()
    enter_manager_telegram_id = State()
    confirm_add_manager = State()
    
    # Состояния для удаления менеджера
    select_manager_to_delete = State()
    confirm_delete_manager = State()

# Функции-обертки для работы с менеджерами
def add_manager(name: str, telegram_id: int) -> bool:
    """Добавить менеджера"""
    if str(telegram_id) not in managers_db:
        add_person(managers_db, name, telegram_id)
        return True
    return False

def remove_manager(manager_id: str) -> bool:
    """Удалить менеджера"""
    return remove_person(managers_db, manager_id)

# Генерируем обработчики для менеджеров
generate_person_entity_handlers(
    router=router,
    entity_name="менеджер",
    entity_name_accusative="менеджера",
    callback_prefix="manager",
    data_storage=managers_db,
    states_class=AdminManagersStates,
    add_function=add_manager
)
