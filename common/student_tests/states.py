from aiogram.fsm.state import State, StatesGroup

class StudentTestsStates(StatesGroup):
    """Состояния для работы с тестами"""
    # Общие состояния
    main = State()  # Главное меню тестов
    test_result = State()  # Просмотр результатов теста
    test_in_progress = State()  # Прохождение теста

    # Состояния для входного теста курса
    course_entry_subjects = State()  # Выбор предмета для входного теста курса
    course_entry_subject_selected = State()  # Предмет выбран, показ результата или запуск теста

    # Состояния для входного теста месяца
    month_entry_subjects = State()  # Выбор предмета для входного теста месяца
    month_entry_subject_selected = State()  # Предмет выбран, выбор месяца
    month_entry_month_selected = State()  # Месяц выбран, показ результата или запуск теста

    # Состояния для контрольного теста месяца
    month_control_subjects = State()  # Выбор предмета для контрольного теста месяца
    month_control_subject_selected = State()  # Предмет выбран, выбор месяца
    month_control_month_selected = State()  # Месяц выбран, показ результата или запуск теста