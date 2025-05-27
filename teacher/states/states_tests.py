from common.tests_statistics import show_tests_statistics_menu
from common.tests_statistics.states import TestsStatisticsStates
from teacher.handlers.tests import (
    show_teacher_tests_statistics
)

# Словарь переходов между состояниями
STATE_TRANSITIONS = {
    TestsStatisticsStates.main: None,  # None означает возврат в главное меню
    TestsStatisticsStates.select_group: TestsStatisticsStates.main,
    TestsStatisticsStates.select_month: TestsStatisticsStates.main,
    TestsStatisticsStates.select_student: TestsStatisticsStates.main,
    TestsStatisticsStates.statistics_result: TestsStatisticsStates.main
}

# Словарь обработчиков для каждого состояния
STATE_HANDLERS = {
    TestsStatisticsStates.main: show_teacher_tests_statistics
    # Остальные обработчики будут использоваться из общего модуля
}