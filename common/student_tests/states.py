from aiogram.fsm.state import State, StatesGroup

class StudentTestsStates(StatesGroup):
    """Состояния для работы с тестами"""
    # Общие состояния
    main = State()  # Главное меню тестов
    test_result = State()  # Просмотр результатов теста (общее, для обратной совместимости)
    test_in_progress = State()  # Прохождение теста

    # Отдельные состояния для результатов разных типов тестов
    course_entry_result = State()  # Результат входного теста курса
    month_entry_result = State()  # Результат входного теста месяца
    month_control_result = State()  # Результат контрольного теста месяца

    # Состояния для входного теста курса
    course_entry_subjects = State()  # Выбор предмета для входного теста курса
    course_entry_subject_selected = State()  # Предмет выбран, показ результата или запуск теста
    course_entry_confirmation = State()  # Подтверждение начала входного теста курса

    # Состояния для входного теста месяца
    month_entry_subjects = State()  # Выбор предмета для входного теста месяца
    month_entry_subject_selected = State()  # Предмет выбран, выбор месяца
    month_entry_month_selected = State()  # Месяц выбран, показ результата или запуск теста
    month_entry_confirmation = State()  # Подтверждение начала входного теста месяца

    # Состояния для контрольного теста месяца
    month_control_subjects = State()  # Выбор предмета для контрольного теста месяца
    month_control_subject_selected = State()  # Предмет выбран, выбор месяца
    month_control_month_selected = State()  # Месяц выбран, показ результата или запуск теста
    month_control_confirmation = State()  # Подтверждение начала контрольного теста месяца