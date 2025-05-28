import logging
from aiogram import Router
from curator.states.states_tests import CuratorTestsStatisticsStates, STATE_TRANSITIONS, STATE_HANDLERS
from common.tests_statistics.register_handlers import register_test_statistics_handlers

# Настраиваем логгер
logger = logging.getLogger(__name__)

router = Router()

# Регистрируем обработчики для куратора
register_test_statistics_handlers(router, CuratorTestsStatisticsStates, "curator")
