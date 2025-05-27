from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
import logging
from common.tests_statistics.states import TestsStatisticsStates
from common.tests_statistics.menu import show_tests_statistics_menu

# Настройка логгера
logger = logging.getLogger(__name__)

# Используем базовые состояния из common.tests_statistics
class TeacherTestsStatisticsStates(TestsStatisticsStates):
    pass

router = Router()

@router.callback_query(F.data == "teacher_tests")
async def show_teacher_tests_statistics(callback: CallbackQuery, state: FSMContext):
    """Показать меню статистики тестов преподавателя"""
    logger.info(f"Вызвана функция show_teacher_tests_statistics для пользователя {callback.from_user.id}")
    await show_tests_statistics_menu(callback, state, "teacher")