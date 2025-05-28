import logging
from aiogram import Router
from teacher.states.states_tests import TeacherTestsStatisticsStates, STATE_TRANSITIONS, STATE_HANDLERS
from common.tests_statistics.register_handlers import register_test_statistics_handlers

# Настройка логгера
logger = logging.getLogger(__name__)

router = Router()

# Регистрируем обработчики для учителя
register_test_statistics_handlers(router, TeacherTestsStatisticsStates, "teacher")
