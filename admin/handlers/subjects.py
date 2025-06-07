from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from admin.utils.common import subjects_db, add_subject, remove_subject
from admin.utils.handlers_generator import generate_simple_entity_handlers

router = Router()

class AdminSubjectsStates(StatesGroup):
    # Состояния для добавления предмета
    enter_subject_name = State()
    confirm_add_subject = State()
    
    # Состояния для удаления предмета
    select_subject_to_delete = State()
    confirm_delete_subject = State()

# Генерируем обработчики для предметов
generate_simple_entity_handlers(
    router=router,
    entity_name="предмет",
    entity_name_accusative="предмет", 
    callback_prefix="subject",
    data_storage=subjects_db,
    add_function=add_subject,
    remove_function=remove_subject,
    states_class=AdminSubjectsStates
)
