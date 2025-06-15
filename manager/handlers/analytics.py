from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from common.analytics.handlers import (
    select_group_for_student_analytics,
    select_student_for_analytics, select_group_for_group_analytics,
    show_subject_microtopics_detailed, show_subject_microtopics_summary
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
    curators_kb = await get_curators_kb()
    await callback.message.edit_text(
        "Выберите куратора:",
        reply_markup=curators_kb
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
    curators_kb = await get_curators_kb()
    await callback.message.edit_text(
        "Выберите куратора:",
        reply_markup=curators_kb
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
    subjects_kb = await get_subjects_kb()
    await callback.message.edit_text(
        "Выберите предмет для просмотра статистики:",
        reply_markup=subjects_kb
    )
    await state.set_state(ManagerAnalyticsStates.select_subject)

@router.callback_query(ManagerAnalyticsStates.select_subject, F.data.startswith("manager_subject_"))
async def manager_show_subject_analytics(callback: CallbackQuery, state: FSMContext):
    """Показать статистику по предмету"""
    logger.info("Вызван обработчик manager_show_subject_analytics")
    subject_id = callback.data.replace("manager_subject_", "")
    logger.debug(f"Выбран предмет с ID: {subject_id}")

    # Получаем данные о предмете
    subject_data = await get_subject_stats(subject_id)

    # Формируем базовую информацию о предмете (как в общей функции)
    result_text = f"📚 Предмет: {subject_data['name']}\n\n"
    result_text += f"👨‍👩‍👧‍👦 Количество групп: {len(subject_data['groups'])}\n"

    if subject_data['groups']:
        # Вычисляем средний процент выполнения ДЗ
        avg_homework = sum(group['homework_completion'] for group in subject_data['groups']) / len(subject_data['groups'])
        result_text += f"📊 Средний % выполнения ДЗ: {avg_homework:.1f}%\n\n"

        # Показываем список групп
        result_text += "📋 Группы:\n"
        for group in subject_data['groups']:
            result_text += f"• {group['name']} - {group['homework_completion']}%\n"
    else:
        result_text += "❌ Группы не найдены\n"

    result_text += "\nВыберите, что хотите посмотреть:"

    # Импортируем клавиатуру
    from common.analytics.keyboards import get_subject_microtopics_kb

    await callback.message.edit_text(
        result_text,
        reply_markup=get_subject_microtopics_kb(int(subject_id))
    )
    await state.set_state(ManagerAnalyticsStates.subject_stats)

# Обработчик для общей статистики
@router.callback_query(ManagerAnalyticsStates.main, F.data == "general_analytics")
async def manager_show_general_analytics(callback: CallbackQuery, state: FSMContext):
    """Показать общую статистику"""
    logger.info("Вызван обработчик manager_show_general_analytics")
    # Получаем общие данные из общего компонента (теперь асинхронно)
    general_data = await get_general_stats()

    # Форматируем статистику в текст
    result_text = format_general_stats(general_data)

    await callback.message.edit_text(
        result_text,
        reply_markup=get_back_to_analytics_kb()
    )
    await state.set_state(ManagerAnalyticsStates.general_stats)

# Обработчики для детальной статистики по микротемам предмета
@router.callback_query(F.data.startswith("subject_microtopics_detailed_"))
async def manager_show_subject_microtopics_detailed(callback: CallbackQuery, state: FSMContext):
    """Показать детальную статистику по микротемам предмета"""
    logger.info("Вызван обработчик manager_show_subject_microtopics_detailed")
    await show_subject_microtopics_detailed(callback, state)

@router.callback_query(F.data.startswith("subject_microtopics_summary_"))
async def manager_show_subject_microtopics_summary(callback: CallbackQuery, state: FSMContext):
    """Показать сводку по сильным и слабым темам предмета"""
    logger.info("Вызван обработчик manager_show_subject_microtopics_summary")
    await show_subject_microtopics_summary(callback, state)