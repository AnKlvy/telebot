from aiogram.fsm.state import StatesGroup, State

class GroupStates(StatesGroup):
    """Базовые состояния для работы с группами"""
    select_group = State()
    select_student = State()
    student_profile = State()