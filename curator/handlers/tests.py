import logging

# Настраиваем логгер
logger = logging.getLogger(__name__)

from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from common.tests_statistics.menu import show_tests_statistics_menu
from common.tests_statistics.handlers import (
    show_tests_comparison, show_month_entry_statistics, show_month_entry_student_statistics, show_course_entry_groups,
    show_month_entry_groups, show_month_entry_months, show_course_entry_student_statistics,
    show_course_entry_statistics, show_month_control_groups, show_month_control_months, show_month_control_statistics,
    show_ent_groups, show_ent_students, show_ent_statistics
)

# Используем конкретные состояния для куратора
class CuratorTestsStatisticsStates(StatesGroup):
    main = State()
    select_group = State()
    select_month = State()
    select_student = State()
    statistics_result = State()

router = Router()

@router.callback_query(F.data == "curator_tests")
async def show_curator_tests_statistics(callback: CallbackQuery, state: FSMContext):
    """Показать меню статистики тестов куратора"""
    logger.info(f"Вызвана функция show_curator_tests_statistics для пользователя {callback.from_user.id}")
    await show_tests_statistics_menu(callback, state, "curator")
    await state.set_state(CuratorTestsStatisticsStates.main)

# Обработчики для входного теста курса
@router.callback_query(CuratorTestsStatisticsStates.main, F.data == "stats_course_entry_test")
async def curator_show_course_entry_groups(callback: CallbackQuery, state: FSMContext):
    """Показать группы для входного теста курса"""
    logger.info(f"Вызвана функция curator_show_course_entry_groups для пользователя {callback.from_user.id}")
    await show_course_entry_groups(callback, state)
    await state.set_state(CuratorTestsStatisticsStates.select_group)

@router.callback_query(CuratorTestsStatisticsStates.select_group, F.data.startswith("course_entry_group_"))
async def curator_show_course_entry_statistics(callback: CallbackQuery, state: FSMContext):
    """Показать статистику входного теста курса для группы"""
    logger.info(f"Вызвана функция curator_show_course_entry_statistics для пользователя {callback.from_user.id}")
    await show_course_entry_statistics(callback, state)
    await state.set_state(CuratorTestsStatisticsStates.statistics_result)

@router.callback_query(F.data.startswith("course_entry_student_"))
async def curator_show_course_entry_student_statistics(callback: CallbackQuery, state: FSMContext):
    """Показать статистику входного теста курса для конкретного ученика"""
    logger.info(f"Вызвана функция curator_show_course_entry_student_statistics для пользователя {callback.from_user.id}")
    await show_course_entry_student_statistics(callback, state)
    await state.set_state(CuratorTestsStatisticsStates.statistics_result)

# Обработчики для входного теста месяца
@router.callback_query(CuratorTestsStatisticsStates.main, F.data == "stats_month_entry_test")
async def curator_show_month_entry_groups(callback: CallbackQuery, state: FSMContext):
    """Показать группы для входного теста месяца"""
    logger.info(f"Вызвана функция curator_show_month_entry_groups для пользователя {callback.from_user.id}")
    await show_month_entry_groups(callback, state)
    await state.set_state(CuratorTestsStatisticsStates.select_group)

@router.callback_query(CuratorTestsStatisticsStates.select_group, F.data.startswith("month_entry_group_"))
async def curator_show_month_entry_months(callback: CallbackQuery, state: FSMContext):
    """Показать месяцы для входного теста месяца"""
    logger.info(f"Вызвана функция curator_show_month_entry_months для пользователя {callback.from_user.id}")
    await show_month_entry_months(callback, state)
    await state.set_state(CuratorTestsStatisticsStates.select_month)

@router.callback_query(F.data.startswith("back_to_month_entry_groups"))
async def curator_back_to_month_entry_groups(callback: CallbackQuery, state: FSMContext):
    """Вернуться к выбору группы для входного теста месяца"""
    logger.info(f"Вызвана функция curator_back_to_month_entry_groups для пользователя {callback.from_user.id}")
    await curator_show_month_entry_groups(callback, state)
    await state.set_state(CuratorTestsStatisticsStates.select_group)

@router.callback_query(CuratorTestsStatisticsStates.select_month, F.data.startswith("month_entry_month_"))
async def curator_show_month_entry_statistics(callback: CallbackQuery, state: FSMContext):
    logger.info(f"Вызвана функция curator_show_month_entry_statistics для пользователя {callback.from_user.id}")
    await show_month_entry_statistics(callback, state)
    await state.set_state(CuratorTestsStatisticsStates.statistics_result)

@router.callback_query(F.data.startswith("month_entry_student_"))
async def curator_show_month_entry_student_statistics(callback: CallbackQuery, state: FSMContext):
    logger.info(f"Вызвана функция curator_show_month_entry_student_statistics для пользователя {callback.from_user.id}")
    await show_month_entry_student_statistics(callback, state)

# Обработчики для контрольного теста месяца
@router.callback_query(CuratorTestsStatisticsStates.main, F.data == "stats_month_control_test")
async def curator_show_month_control_groups(callback: CallbackQuery, state: FSMContext):
    """Показать группы для контрольного теста месяца"""
    logger.info(f"Вызвана функция curator_show_month_control_groups для пользователя {callback.from_user.id}")
    await show_month_control_groups(callback, state)
    await state.set_state(CuratorTestsStatisticsStates.select_group)

@router.callback_query(CuratorTestsStatisticsStates.select_group, F.data.startswith("month_control_group_"))
async def curator_show_month_control_months(callback: CallbackQuery, state: FSMContext):
    """Показать месяцы для контрольного теста месяца"""
    logger.info(f"Вызвана функция curator_show_month_control_months для пользователя {callback.from_user.id}")
    await show_month_control_months(callback, state)
    await state.set_state(CuratorTestsStatisticsStates.select_month)

@router.callback_query(F.data.startswith("back_to_month_control_groups"))
async def curator_back_to_month_control_groups(callback: CallbackQuery, state: FSMContext):
    """Вернуться к выбору группы для контрольного теста месяца"""
    logger.info(f"Вызвана функция curator_back_to_month_control_groups для пользователя {callback.from_user.id}")
    await curator_show_month_control_groups(callback, state)

@router.callback_query(CuratorTestsStatisticsStates.select_month, F.data.startswith("month_control_month_"))
async def curator_show_month_control_statistics(callback: CallbackQuery, state: FSMContext):
    """Показать статистику контрольного теста месяца"""
    logger.info(f"Вызвана функция curator_show_month_control_statistics для пользователя {callback.from_user.id}")
    await show_month_control_statistics(callback, state)
    await state.set_state(CuratorTestsStatisticsStates.statistics_result)

@router.callback_query(F.data.startswith("month_control_student_"))
async def curator_show_month_control_student_statistics(callback: CallbackQuery, state: FSMContext):
    """Показать статистику контрольного теста месяца для конкретного ученика"""
    logger.info(f"Вызвана функция curator_show_month_control_student_statistics для пользователя {callback.from_user.id}")
    await show_tests_comparison(callback, state)
    await state.set_state(CuratorTestsStatisticsStates.statistics_result)

# Обработчики для пробного ЕНТ
@router.callback_query(CuratorTestsStatisticsStates.main, F.data == "stats_ent_test")
async def curator_show_ent_groups(callback: CallbackQuery, state: FSMContext):
    """Показать группы для пробного ЕНТ"""
    logger.info(f"Вызвана функция curator_show_ent_groups для пользователя {callback.from_user.id}")
    await show_ent_groups(callback, state)
    await state.set_state(CuratorTestsStatisticsStates.select_group)

@router.callback_query(CuratorTestsStatisticsStates.select_group, F.data.startswith("ent_group_"))
async def curator_show_ent_students(callback: CallbackQuery, state: FSMContext):
    """Показать студентов для пробного ЕНТ"""
    logger.info(f"Вызвана функция curator_show_ent_students для пользователя {callback.from_user.id}")
    await show_ent_students(callback, state)
    await state.set_state(CuratorTestsStatisticsStates.select_student)

@router.callback_query(F.data.startswith("back_to_ent_groups"))
async def curator_back_to_ent_groups(callback: CallbackQuery, state: FSMContext):
    """Вернуться к выбору группы для пробного ЕНТ"""
    logger.info(f"Вызвана функция curator_back_to_ent_groups для пользователя {callback.from_user.id}")
    await curator_show_ent_groups(callback, state)
    await state.set_state(CuratorTestsStatisticsStates.select_group)

@router.callback_query(CuratorTestsStatisticsStates.select_student, F.data.startswith("ent_student_"))
async def curator_show_ent_statistics(callback: CallbackQuery, state: FSMContext):
    """Показать статистику пробного ЕНТ для студента"""
    logger.info(f"Вызвана функция curator_show_ent_statistics для пользователя {callback.from_user.id}")
    await show_ent_statistics(callback, state)
    await state.set_state(CuratorTestsStatisticsStates.statistics_result)