from aiogram.fsm.state import StatesGroup, State
from common.tests_statistics.register_handlers import get_transitions_handlers

# Используем конкретные состояния для куратора
class CuratorTestsStatisticsStates(StatesGroup):
    main = State()
    
    # Состояния для входного теста курса
    course_entry_select_group = State()
    course_entry_result = State()
    
    # Состояния для входного теста месяца
    month_entry_select_group = State()
    month_entry_select_month = State()
    month_entry_result = State()
    
    # Состояния для контрольного теста месяца
    month_control_select_group = State()
    month_control_select_month = State()
    month_control_result = State()
    
    # Состояния для пробного ЕНТ
    ent_select_group = State()
    ent_select_student = State()
    ent_result = State()

# Создаем словари переходов и обработчиков для куратора
STATE_TRANSITIONS, STATE_HANDLERS = get_transitions_handlers(CuratorTestsStatisticsStates, "curator")
