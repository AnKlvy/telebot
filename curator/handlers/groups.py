from aiogram import Router
from aiogram.fsm.state import StatesGroup, State
from common.groups.register_handlers import register_groups_handlers

# Используем конкретные состояния для куратора
class CuratorGroupStates(StatesGroup):
    select_group = State()
    select_student = State()
    student_profile = State()

router = Router()

# Регистрируем обработчики для куратора
register_groups_handlers(router, CuratorGroupStates, "curator")
