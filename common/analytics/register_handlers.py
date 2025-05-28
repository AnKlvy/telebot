import logging
from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from common.analytics.handlers import (
    show_analytics_menu, select_group_for_student_analytics,
    select_student_for_analytics, show_student_analytics,
    select_group_for_group_analytics, show_group_analytics
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
        await state.set_state(states_group.select_student)

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
