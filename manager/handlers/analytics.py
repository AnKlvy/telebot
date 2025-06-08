from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from common.analytics.handlers import (
    select_group_for_student_analytics,
    select_student_for_analytics, select_group_for_group_analytics
)
from ..keyboards.analytics import (
    get_manager_analytics_menu_kb, get_curators_kb, get_subjects_kb
)
from common.analytics.keyboards import get_back_to_analytics_kb
from common.statistics import (
    get_subject_stats, format_subject_stats, get_general_stats, format_general_stats, show_student_analytics,
    show_group_analytics
)
from common.utils import check_if_id_in_callback_data
import logging

# Настройка логгера
logger = logging.getLogger(__name__)

# Расширяем базовые состояния для менеджера
class ManagerAnalyticsStates(StatesGroup):
    main = State()
    select_group_for_student = State()
    select_student = State()
    select_group_for_group = State()
    select_curator_for_student = State()
    select_curator_for_group = State()
    select_subject = State()
    subject_stats = State()
    student_stats = State()
    group_stats = State()
    general_stats = State()

router = Router()

@router.callback_query(F.data == "manager_analytics")
async def show_manager_analytics_menu(callback: CallbackQuery, state: FSMContext):
    """Показать меню аналитики менеджера"""
    logger.info("Вызван обработчик show_manager_analytics_menu")
    await callback.message.edit_text(
        "Выберите тип аналитики:",
        reply_markup=get_manager_analytics_menu_kb()
    )
    await state.set_state(ManagerAnalyticsStates.main)

# Обработчики для статистики по ученику
@router.callback_query(ManagerAnalyticsStates.main, F.data == "manager_student_analytics")
async def manager_select_curator_for_student(callback: CallbackQuery, state: FSMContext):
    """Выбор куратора для статистики по ученику"""
    logger.info("Вызван обработчик manager_select_curator_for_student")
    await callback.message.edit_text(
        "Выберите куратора:",
        reply_markup=get_curators_kb()
    )
    await state.set_state(ManagerAnalyticsStates.select_curator_for_student)

@router.callback_query(ManagerAnalyticsStates.select_curator_for_student, F.data.startswith("manager_curator_"))
async def manager_select_group_for_student(callback: CallbackQuery, state: FSMContext):
    """Выбор группы для статистики по ученику"""
    logger.info("Вызван обработчик manager_select_group_for_student")
    curator_id = await check_if_id_in_callback_data("manager_curator_", callback, state, "curator")
    logger.debug(f"Выбран куратор с ID: {curator_id}")
    await state.update_data(selected_curator=curator_id)
    await select_group_for_student_analytics(callback, state, "manager")
    await state.set_state(ManagerAnalyticsStates.select_group_for_student)

@router.callback_query(ManagerAnalyticsStates.select_group_for_student, F.data.startswith("analytics_group_"))
async def manager_select_student_for_analytics(callback: CallbackQuery, state: FSMContext):
    """Выбор ученика для статистики"""
    logger.info("Вызван обработчик manager_select_student_for_analytics")
    await select_student_for_analytics(callback, state, "manager")
    await state.set_state(ManagerAnalyticsStates.select_student)

@router.callback_query(ManagerAnalyticsStates.select_student, F.data.startswith("analytics_student_"))
async def manager_show_student_analytics(callback: CallbackQuery, state: FSMContext):
    """Показать статистику по ученику"""
    logger.info("Вызван обработчик manager_show_student_analytics")
    await show_student_analytics(callback, state, "manager")

# Обработчики для статистики по группе
@router.callback_query(ManagerAnalyticsStates.main, F.data == "manager_group_analytics")
async def manager_select_curator_for_group(callback: CallbackQuery, state: FSMContext):
    """Выбор куратора для статистики по группе"""
    logger.info("Вызван обработчик manager_select_curator_for_group")
    await callback.message.edit_text(
        "Выберите куратора:",
        reply_markup=get_curators_kb()
    )
    await state.set_state(ManagerAnalyticsStates.select_curator_for_group)

@router.callback_query(ManagerAnalyticsStates.select_curator_for_group, F.data.startswith("manager_curator_"))
async def manager_select_group_for_group(callback: CallbackQuery, state: FSMContext):
    """Выбор группы для статистики по группе"""
    logger.info("Вызван обработчик manager_select_group_for_group")
    curator_id = callback.data.replace("manager_curator_", "")
    logger.debug(f"Выбран куратор с ID: {curator_id}")
    await state.update_data(selected_curator=curator_id)
    
    await select_group_for_group_analytics(callback, state, "manager")
    await state.set_state(ManagerAnalyticsStates.select_group_for_group)

@router.callback_query(ManagerAnalyticsStates.select_group_for_group, F.data.startswith("analytics_group_"))
async def manager_show_group_analytics(callback: CallbackQuery, state: FSMContext):
    """Показать статистику по группе"""
    logger.info("Вызван обработчик manager_show_group_analytics")
    await show_group_analytics(callback, state, "manager")

# Обработчики для статистики по предмету
@router.callback_query(ManagerAnalyticsStates.main, F.data == "manager_subject_analytics")
async def manager_select_subject(callback: CallbackQuery, state: FSMContext):
    """Выбор предмета для статистики"""
    logger.info("Вызван обработчик manager_select_subject")
    await callback.message.edit_text(
        "Выберите предмет для просмотра статистики:",
        reply_markup=get_subjects_kb()
    )
    await state.set_state(ManagerAnalyticsStates.select_subject)

@router.callback_query(ManagerAnalyticsStates.select_subject, F.data.startswith("manager_subject_"))
async def manager_show_subject_analytics(callback: CallbackQuery, state: FSMContext):
    """Показать статистику по предмету"""
    logger.info("Вызван обработчик manager_show_subject_analytics")
    subject_id = callback.data.replace("manager_subject_", "")
    logger.debug(f"Выбран предмет с ID: {subject_id}")
    
    # Получаем данные о предмете из общего компонента
    subject_data = get_subject_stats(subject_id)
    
    # Форматируем статистику в текст
    result_text = format_subject_stats(subject_data)
    
    await callback.message.edit_text(
        result_text,
        reply_markup=get_back_to_analytics_kb()
    )
    await state.set_state(ManagerAnalyticsStates.subject_stats)

# Обработчик для общей статистики
@router.callback_query(ManagerAnalyticsStates.main, F.data == "general_analytics")
async def manager_show_general_analytics(callback: CallbackQuery, state: FSMContext):
    """Показать общую статистику"""
    logger.info("Вызван обработчик manager_show_general_analytics")
    # Получаем общие данные из общего компонента
    general_data = get_general_stats()
    
    # Форматируем статистику в текст
    result_text = format_general_stats(general_data)
    
    await callback.message.edit_text(
        result_text,
        reply_markup=get_back_to_analytics_kb()
    )
    await state.set_state(ManagerAnalyticsStates.general_stats)