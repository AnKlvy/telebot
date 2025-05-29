from aiogram import Router
from aiogram.fsm.state import State, StatesGroup
from common.groups.register_handlers import register_groups_handlers

# Используем базовые состояния
class TeacherGroupStates(StatesGroup):
    """Состояния для работы с группами для учителя"""
    select_group = State()
    select_student = State()
    student_profile = State()

router = Router()

# Регистрируем обработчики для учителя
register_groups_handlers(router, TeacherGroupStates, "teacher")
