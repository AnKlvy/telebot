import logging
from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from common.analytics.handlers import (
    show_analytics_menu, select_group_for_student_analytics,
    select_student_for_analytics, select_group_for_group_analytics,
    show_microtopics_detailed, show_microtopics_summary, back_to_student_analytics,
    select_subject_for_analytics, show_subject_analytics,
    show_subject_microtopics_detailed, show_subject_microtopics_summary
)
from common.statistics import (
    show_student_analytics, show_group_analytics,
    show_group_microtopics_detailed, show_group_rating
)


# Настройка логирования
logging.basicConfig(level=logging.INFO)

def register_analytics_handlers(router, states_group, role):
    """Регистрация обработчиков аналитики"""
    @router.callback_query(F.data == f"{role}_analytics")
    async def show_role_analytics_menu(callback: CallbackQuery, state: FSMContext):
        logging.info(f"ВЫЗОВ: show_role_analytics_menu | КОЛБЭК: {callback.data} | СОСТОЯНИЕ: {await state.get_state()}")
        await show_analytics_menu(callback, state, role)
        await state.set_state(states_group.main)


    @router.callback_query(states_group.select_group_for_student, F.data.startswith("analytics_group_"))
    async def role_select_student_for_student_state(callback: CallbackQuery, state: FSMContext):
        logging.info(f"ВЫЗОВ: role_select_student_for_student_state | КОЛБЭК: {callback.data} | СОСТОЯНИЕ: {await state.get_state()}")
        await select_student_for_analytics(callback, state, role)
        await state.set_state(states_group.select_student)

    @router.callback_query(states_group.select_group_for_group, F.data.startswith("analytics_group_"))
    async def role_select_student_for_group(callback: CallbackQuery, state: FSMContext):
        logging.info(f"ВЫЗОВ: role_select_student_for_group_state | КОЛБЭК: {callback.data} | СОСТОЯНИЕ: {await state.get_state()}")
        await show_group_analytics(callback, state, role)
        await state.set_state(states_group.group_stats)

    @router.callback_query(states_group.select_student, F.data.startswith("analytics_student_"))
    async def role_show_student_stats(callback: CallbackQuery, state: FSMContext):
        logging.info(f"ВЫЗОВ: role_show_student_stats | КОЛБЭК: {callback.data} | СОСТОЯНИЕ: {await state.get_state()}")
        await show_student_analytics(callback, state, role)
        await state.set_state(states_group.student_stats)

    @router.callback_query(states_group.main, F.data == "group_analytics")
    async def role_select_group_for_group(callback: CallbackQuery, state: FSMContext):
        logging.info(f"ВЫЗОВ: role_select_group_for_group | КОЛБЭК: {callback.data} | СОСТОЯНИЕ: {await state.get_state()}")
        await select_group_for_group_analytics(callback, state, role)
        await state.set_state(states_group.select_group_for_group)

    @router.callback_query(states_group.main, F.data == "student_analytics")
    async def role_select_group_for_student(callback: CallbackQuery, state: FSMContext):
        logging.info(f"ВЫЗОВ: role_select_group_for_student | КОЛБЭК: {callback.data} | СОСТОЯНИЕ: {await state.get_state()}")
        await select_group_for_student_analytics(callback, state, role)
        await state.set_state(states_group.select_group_for_student)

    # Обработчики для новых кнопок статистики по микротемам студентов (с фильтрацией по состояниям)
    @router.callback_query(states_group.student_stats, F.data.startswith("microtopics_detailed_"))
    async def role_show_microtopics_detailed(callback: CallbackQuery, state: FSMContext):
        logging.info(f"ВЫЗОВ: role_show_microtopics_detailed | КОЛБЭК: {callback.data} | СОСТОЯНИЕ: {await state.get_state()}")
        await show_microtopics_detailed(callback, state)
        # Переходим в состояние отображения статистики студента
        await state.set_state(states_group.student_stats_display)

    @router.callback_query(states_group.student_stats, F.data.startswith("microtopics_summary_"))
    async def role_show_microtopics_summary(callback: CallbackQuery, state: FSMContext):
        logging.info(f"ВЫЗОВ: role_show_microtopics_summary | КОЛБЭК: {callback.data} | СОСТОЯНИЕ: {await state.get_state()}")
        await show_microtopics_summary(callback, state)
        # Переходим в состояние отображения статистики студента
        await state.set_state(states_group.student_stats_display)

    @router.callback_query(F.data.startswith("back_to_student_"))
    async def role_back_to_student_analytics(callback: CallbackQuery, state: FSMContext):
        logging.info(f"ВЫЗОВ: role_back_to_student_analytics | КОЛБЭК: {callback.data} | СОСТОЯНИЕ: {await state.get_state()}")
        await back_to_student_analytics(callback, state, role)

    # Обработчики для статистики по предмету
    @router.callback_query(states_group.main, F.data == "subject_analytics")
    async def role_select_subject_for_analytics(callback: CallbackQuery, state: FSMContext):
        logging.info(f"ВЫЗОВ: role_select_subject_for_analytics | КОЛБЭК: {callback.data} | СОСТОЯНИЕ: {await state.get_state()}")
        await select_subject_for_analytics(callback, state, role)
        await state.set_state(states_group.select_subject)

    @router.callback_query(states_group.select_subject, F.data.startswith("analytics_subject_"))
    async def role_show_subject_analytics(callback: CallbackQuery, state: FSMContext):
        logging.info(f"ВЫЗОВ: role_show_subject_analytics | КОЛБЭК: {callback.data} | СОСТОЯНИЕ: {await state.get_state()}")
        await show_subject_analytics(callback, state, role)
        await state.set_state(states_group.subject_stats)

    # Обработчики для детальной статистики по микротемам предмета (с фильтрацией по состояниям)
    @router.callback_query(states_group.subject_stats, F.data.startswith("subject_microtopics_detailed_"))
    async def role_show_subject_microtopics_detailed(callback: CallbackQuery, state: FSMContext):
        logging.info(f"ВЫЗОВ: role_show_subject_microtopics_detailed | КОЛБЭК: {callback.data} | СОСТОЯНИЕ: {await state.get_state()}")
        await show_subject_microtopics_detailed(callback, state)

    @router.callback_query(states_group.subject_stats, F.data.startswith("subject_microtopics_summary_"))
    async def role_show_subject_microtopics_summary(callback: CallbackQuery, state: FSMContext):
        logging.info(f"ВЫЗОВ: role_show_subject_microtopics_summary | КОЛБЭК: {callback.data} | СОСТОЯНИЕ: {await state.get_state()}")
        await show_subject_microtopics_summary(callback, state)

    # Обработчики для статистики по группам (с фильтрацией по состояниям)
    @router.callback_query(states_group.group_stats, F.data.startswith("group_microtopics_detailed_"))
    async def role_show_group_microtopics_detailed(callback: CallbackQuery, state: FSMContext):
        logging.info(f"ВЫЗОВ: role_show_group_microtopics_detailed | КОЛБЭК: {callback.data} | СОСТОЯНИЕ: {await state.get_state()}")
        await show_group_microtopics_detailed(callback, state)
        # Переходим в состояние отображения статистики группы
        await state.set_state(states_group.group_stats_display)

    @router.callback_query(states_group.group_stats, F.data.startswith("group_rating_"))
    async def role_show_group_rating(callback: CallbackQuery, state: FSMContext):
        logging.info(f"ВЫЗОВ: role_show_group_rating | КОЛБЭК: {callback.data} | СОСТОЯНИЕ: {await state.get_state()}")
        await show_group_rating(callback, state)
        # Переходим в состояние отображения статистики группы
        await state.set_state(states_group.group_stats_display)
