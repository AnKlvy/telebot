from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from common.groups.handlers import show_groups, show_group_students, show_student_profile

# Используем конкретные состояния для куратора
class CuratorGroupStates(StatesGroup):
    select_group = State()
    select_student = State()
    student_profile = State()

router = Router()

@router.callback_query(F.data == "curator_my_group")
async def show_curator_groups(callback: CallbackQuery, state: FSMContext):
    """Показать список групп куратора"""
    await show_groups(callback, state, "curator")
    await state.set_state(CuratorGroupStates.select_group)

@router.callback_query(CuratorGroupStates.select_group, F.data.startswith("curator_group_"))
async def show_curator_group_students(callback: CallbackQuery, state: FSMContext):
    """Показать студентов группы куратора"""
    await show_group_students(callback, state, "curator")
    await state.set_state(CuratorGroupStates.select_student)

@router.callback_query(CuratorGroupStates.select_student, F.data.startswith("curator_student_"))
async def show_curator_student_profile(callback: CallbackQuery, state: FSMContext):
    """Показать профиль студента для куратора"""
    await show_student_profile(callback, state, "curator")
    await state.set_state(CuratorGroupStates.student_profile)
