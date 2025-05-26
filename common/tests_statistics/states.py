from aiogram.fsm.state import State, StatesGroup

class TestsStatisticsStates(StatesGroup):
    """Состояния для работы со статистикой тестов"""
    main = State()
    select_group = State()
    select_month = State()
    select_student = State()
    statistics_result = State()