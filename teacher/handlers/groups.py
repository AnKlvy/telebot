from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from common.groups.states import GroupStates
from common.groups.handlers import (
    show_groups, show_student_profile, show_group_students
)

# Используем базовые состояния
class TeacherGroupStates(GroupStates):
    pass

router = Router()

@router.callback_query(F.data == "teacher_my_group")
async def show_teacher_groups(callback: CallbackQuery, state: FSMContext):
    """Показать группы преподавателя"""
    await show_groups(callback, state, "teacher")

@router.callback_query(TeacherGroupStates.select_group, F.data.startswith("teacher_group_"))
async def show_teacher_students(callback: CallbackQuery, state: FSMContext):
    """Показать учеников в группе"""
    await show_group_students(callback, state, "teacher")

@router.callback_query(TeacherGroupStates.select_student, F.data.startswith("teacher_student_"))
async def show_teacher_student_profile(callback: CallbackQuery, state: FSMContext):
    """Показать профиль ученика"""
    await show_student_profile(callback, state, "teacher")