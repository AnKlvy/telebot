import logging
from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from common.groups.handlers import (
    show_groups, show_group_students, show_student_profile
)

# Настройка логирования
logging.basicConfig(level=logging.INFO)

def register_groups_handlers(router: Router, states_group, role: str):
    """Регистрация обработчиков для работы с группами"""
    
    @router.callback_query(F.data == f"{role}_my_group")
    async def show_role_groups(callback: CallbackQuery, state: FSMContext):
        logging.info(f"ВЫЗОВ: show_role_groups | КОЛБЭК: {callback.data} | СОСТОЯНИЕ: {await state.get_state()}")
        await show_groups(callback, state, role)
        await state.set_state(states_group.select_group)

    @router.callback_query(states_group.select_group, F.data.startswith(f"{role}_group_"))
    async def show_role_students(callback: CallbackQuery, state: FSMContext):
        logging.info(f"ВЫЗОВ: show_role_students | КОЛБЭК: {callback.data} | СОСТОЯНИЕ: {await state.get_state()}")
        await show_group_students(callback, state, role)
        await state.set_state(states_group.select_student)

    @router.callback_query(states_group.select_student, F.data.startswith(f"{role}_student_"))
    async def show_role_student_profile(callback: CallbackQuery, state: FSMContext):
        logging.info(f"ВЫЗОВ: show_role_student_profile | КОЛБЭК: {callback.data} | СОСТОЯНИЕ: {await state.get_state()}")
        await show_student_profile(callback, state, role)
        await state.set_state(states_group.student_profile) 