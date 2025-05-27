import logging

# Настраиваем логгер
logger = logging.getLogger(__name__)

from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from common.tests.states import TestsStates
from common.tests_statistics.states import TestsStatisticsStates
from common.tests_statistics.menu import show_tests_statistics_menu
from common.tests_statistics.handlers import (
    show_test_students_statistics,
    show_student_test_statistics,
    show_tests_comparison, show_month_entry_statistics, show_month_entry_student_statistics
)
from common.tests_statistics.keyboards import (
    get_tests_statistics_menu_kb, 
    get_back_kb,
    get_groups_kb,
    get_month_kb,
    get_students_kb
)

# Используем базовые состояния из common.tests_statistics
class CuratorTestsStatisticsStates(TestsStatisticsStates):
    pass

router = Router()

@router.callback_query(F.data == "curator_tests")
async def show_curator_tests_statistics(callback: CallbackQuery, state: FSMContext):
    """Показать меню статистики тестов куратора"""
    logger.info(f"Вызвана функция show_curator_tests_statistics для пользователя {callback.from_user.id}")
    await show_tests_statistics_menu(callback, state, "curator")

# Обработчики для входного теста курса
@router.callback_query(CuratorTestsStatisticsStates.main, F.data == "stats_course_entry_test")
async def curator_show_course_entry_groups(callback: CallbackQuery, state: FSMContext):
    """Показать группы для входного теста курса"""
    logger.info(f"Вызвана функция curator_show_course_entry_groups для пользователя {callback.from_user.id}")
    await callback.message.edit_text(
        "Выберите группу для просмотра статистики входного теста курса:",
        reply_markup=get_groups_kb("course_entry")
    )
    await state.set_state(CuratorTestsStatisticsStates.select_group)

@router.callback_query(CuratorTestsStatisticsStates.select_group, F.data.startswith("course_entry_group_"))
async def curator_show_course_entry_statistics(callback: CallbackQuery, state: FSMContext):
    """Показать статистику входного теста курса для группы"""
    logger.info(f"Вызвана функция curator_show_course_entry_statistics для пользователя {callback.from_user.id}")
    group_id = callback.data.replace("course_entry_group_", "")
    await show_test_students_statistics(callback, state, "course_entry", group_id)

@router.callback_query(F.data.startswith("course_entry_student_"))
async def curator_show_course_entry_student_statistics(callback: CallbackQuery, state: FSMContext):
    """Показать статистику входного теста курса для конкретного ученика"""
    logger.info(f"Вызвана функция curator_show_course_entry_student_statistics для пользователя {callback.from_user.id}")
    # Формат: course_entry_student_GROUP_ID_STUDENT_ID
    parts = callback.data.split("_")
    group_id = parts[3]
    student_id = parts[4]
    await show_student_test_statistics(callback, state, "course_entry", student_id, group_id)

# Обработчики для входного теста месяца
@router.callback_query(CuratorTestsStatisticsStates.main, F.data == "stats_month_entry_test")
async def curator_show_month_entry_groups(callback: CallbackQuery, state: FSMContext):
    """Показать группы для входного теста месяца"""
    logger.info(f"Вызвана функция curator_show_month_entry_groups для пользователя {callback.from_user.id}")
    await callback.message.edit_text(
        "Выберите группу для просмотра статистики входного теста месяца:",
        reply_markup=get_groups_kb("month_entry")
    )
    await state.set_state(CuratorTestsStatisticsStates.select_group)

@router.callback_query(CuratorTestsStatisticsStates.select_group, F.data.startswith("month_entry_group_"))
async def curator_show_month_entry_months(callback: CallbackQuery, state: FSMContext):
    """Показать месяцы для входного теста месяца"""
    logger.info(f"Вызвана функция curator_show_month_entry_months для пользователя {callback.from_user.id}")
    group_id = callback.data.replace("month_entry_group_", "")
    
    await state.update_data(selected_group=group_id)
    
    await callback.message.edit_text(
        "Выберите месяц для просмотра статистики входного теста:",
        reply_markup=get_month_kb("month_entry", group_id)
    )
    await state.set_state(CuratorTestsStatisticsStates.select_month)

@router.callback_query(F.data.startswith("back_to_month_entry_groups"))
async def curator_back_to_month_entry_groups(callback: CallbackQuery, state: FSMContext):
    """Вернуться к выбору группы для входного теста месяца"""
    logger.info(f"Вызвана функция curator_back_to_month_entry_groups для пользователя {callback.from_user.id}")
    await curator_show_month_entry_groups(callback, state)

@router.callback_query(CuratorTestsStatisticsStates.select_month, F.data.startswith("month_entry_month_"))
async def curator_show_month_entry_statistics(callback: CallbackQuery, state: FSMContext):
    logger.info(f"Вызвана функция curator_show_month_entry_statistics для пользователя {callback.from_user.id}")
    await show_month_entry_statistics(callback, state)

@router.callback_query(F.data.startswith("month_entry_student_"))
async def curator_show_month_entry_student_statistics(callback: CallbackQuery, state: FSMContext):
    logger.info(f"Вызвана функция curator_show_month_entry_student_statistics для пользователя {callback.from_user.id}")
    await show_month_entry_student_statistics(callback, state)

# Обработчики для контрольного теста месяца
@router.callback_query(CuratorTestsStatisticsStates.main, F.data == "stats_month_control_test")
async def curator_show_month_control_groups(callback: CallbackQuery, state: FSMContext):
    """Показать группы для контрольного теста месяца"""
    logger.info(f"Вызвана функция curator_show_month_control_groups для пользователя {callback.from_user.id}")
    await callback.message.edit_text(
        "Выберите группу для просмотра статистики контрольного теста месяца:",
        reply_markup=get_groups_kb("month_control")
    )
    await state.set_state(CuratorTestsStatisticsStates.select_group)

@router.callback_query(CuratorTestsStatisticsStates.select_group, F.data.startswith("month_control_group_"))
async def curator_show_month_control_months(callback: CallbackQuery, state: FSMContext):
    """Показать месяцы для контрольного теста месяца"""
    logger.info(f"Вызвана функция curator_show_month_control_months для пользователя {callback.from_user.id}")
    group_id = callback.data.replace("month_control_group_", "")
    
    await state.update_data(selected_group=group_id)
    
    await callback.message.edit_text(
        "Выберите месяц для просмотра статистики контрольного теста:",
        reply_markup=get_month_kb("month_control", group_id)
    )
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
    # Формат: month_control_month_GROUP_ID_MONTH_ID
    parts = callback.data.split("_")
    group_id = parts[3]
    month_id = parts[4]
    await show_test_students_statistics(callback, state, "month_control", group_id, month_id)

@router.callback_query(F.data.startswith("month_control_student_"))
async def curator_show_month_control_student_statistics(callback: CallbackQuery, state: FSMContext):
    """Показать статистику контрольного теста месяца для конкретного ученика"""
    logger.info(f"Вызвана функция curator_show_month_control_student_statistics для пользователя {callback.from_user.id}")
    # Формат: month_control_student_GROUP_ID_MONTH_ID_STUDENT_ID
    parts = callback.data.split("_")
    group_id = parts[3]
    month_id = parts[4]
    student_id = parts[5]
    
    logger.info(f"Параметры: test_type=month_control, student_id={student_id}, group_id={group_id}, month_id={month_id}")
    
    # Получаем результаты теста напрямую для отладки
    from common.statistics import get_test_results
    test_id = f"month_control_chem_{month_id}"
    test_results = get_test_results(test_id, student_id)
    logger.info(f"Результаты теста: {test_results}")
    
    await show_student_test_statistics(callback, state, "month_control", student_id, group_id, month_id)

# Обработчики для пробного ЕНТ
@router.callback_query(CuratorTestsStatisticsStates.main, F.data == "stats_ent_test")
async def curator_show_ent_groups(callback: CallbackQuery, state: FSMContext):
    """Показать группы для пробного ЕНТ"""
    logger.info(f"Вызвана функция curator_show_ent_groups для пользователя {callback.from_user.id}")
    await callback.message.edit_text(
        "Выберите группу для просмотра статистики пробного ЕНТ:",
        reply_markup=get_groups_kb("ent")
    )
    await state.set_state(CuratorTestsStatisticsStates.select_group)

@router.callback_query(CuratorTestsStatisticsStates.select_group, F.data.startswith("ent_group_"))
async def curator_show_ent_students(callback: CallbackQuery, state: FSMContext):
    """Показать студентов для пробного ЕНТ"""
    logger.info(f"Вызвана функция curator_show_ent_students для пользователя {callback.from_user.id}")
    group_id = callback.data.replace("ent_group_", "")
    
    await state.update_data(selected_group=group_id)
    
    await callback.message.edit_text(
        "Выберите ученика для просмотра статистики пробного ЕНТ:",
        reply_markup=get_students_kb("ent", group_id)
    )
    await state.set_state(CuratorTestsStatisticsStates.select_student)

@router.callback_query(F.data.startswith("back_to_ent_groups"))
async def curator_back_to_ent_groups(callback: CallbackQuery, state: FSMContext):
    """Вернуться к выбору группы для пробного ЕНТ"""
    logger.info(f"Вызвана функция curator_back_to_ent_groups для пользователя {callback.from_user.id}")
    await curator_show_ent_groups(callback, state)

@router.callback_query(CuratorTestsStatisticsStates.select_student, F.data.startswith("ent_student_"))
async def curator_show_ent_statistics(callback: CallbackQuery, state: FSMContext):
    """Показать статистику пробного ЕНТ для студента"""
    logger.info(f"Вызвана функция curator_show_ent_statistics для пользователя {callback.from_user.id}")
    # Формат: ent_student_GROUP_ID_STUDENT_ID
    parts = callback.data.split("_")
    group_id = parts[2]
    student_id = parts[3]
    await show_student_test_statistics(callback, state, "ent", student_id, group_id)

# Обработчик для возврата в меню статистики тестов
@router.callback_query(F.data == "back_to_tests_statistics")
async def curator_back_to_tests_statistics(callback: CallbackQuery, state: FSMContext):
    """Вернуться в меню статистики тестов"""
    logger.info(f"Вызвана функция curator_back_to_tests_statistics для пользователя {callback.from_user.id}")
    await show_tests_statistics_menu(callback, state, "curator")