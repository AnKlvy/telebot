from aiogram.fsm.state import State, StatesGroup

class StudentTestsStates(StatesGroup):
    """Состояния для работы с тестами"""
    # Общие состояния
    main = State()
    test_result = State()
    test_in_progress = State()
    
    # Состояния для входного теста курса
    select_group_entry = State()
    
    # Состояния для входного теста месяца
    select_month_entry = State()
    
    # Состояния для контрольного теста месяца
    select_group_control = State()
    select_month_control = State()