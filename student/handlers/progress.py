from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from ..keyboards.progress import get_progress_menu_kb, get_subjects_progress_kb, get_back_to_progress_kb
from common.statistics import get_student_topics_stats, format_student_topics_stats, format_student_topics_stats_real

router = Router()

class ProgressStates(StatesGroup):
    main = State()
    subjects = State()
    common_stats = State()
    subject_details = State()

@router.callback_query(F.data == "progress")
async def show_progress_menu(callback: CallbackQuery, state: FSMContext):
    """Показать меню прогресса"""
    await callback.message.edit_text(
        "Что именно хочешь посмотреть? Выбери один из вариантов:",
        reply_markup=get_progress_menu_kb()
    )
    await state.set_state(ProgressStates.main)

@router.callback_query(ProgressStates.main, F.data == "general_stats")
async def show_general_stats(callback: CallbackQuery, state: FSMContext):
    """Показать общую статистику"""
    # В реальном приложении эти данные будут загружаться из базы данных
    points = 870
    level = "🧪 Практик"
    completed_homeworks = 28
    
    await callback.message.edit_text(
        f"Вот твоя краткая статистика 👇\n"
        f"📊 Баллы: {points}\n"
        f"🎯 Уровень: {level}\n"
        f"📋 Выполнено домашних заданий: {completed_homeworks}",
        reply_markup=get_back_to_progress_kb()
    )
    await state.set_state(ProgressStates.common_stats)

@router.callback_query(ProgressStates.main, F.data == "topics_understanding")
async def show_subjects_list(callback: CallbackQuery, state: FSMContext):
    """Показать список предметов для просмотра понимания по темам"""
    await callback.message.edit_text(
        "Выбери предмет, чтобы посмотреть % понимания по микротемам:",
        reply_markup=get_subjects_progress_kb()
    )
    await state.set_state(ProgressStates.subjects)

@router.callback_query(ProgressStates.subjects, F.data.startswith("progress_sub_"))
async def show_subject_progress(callback: CallbackQuery, state: FSMContext):
    """Показать прогресс по выбранному предмету"""
    subject_id = callback.data.replace("progress_sub_", "")

    # Получаем ID студента из Telegram ID
    from database import StudentRepository
    student = await StudentRepository.get_by_telegram_id(callback.from_user.id)

    if not student:
        await callback.message.edit_text(
            "❌ Студент не найден в системе",
            reply_markup=get_back_to_progress_kb()
        )
        return

    # Используем новую функцию с реальными данными из БД
    progress_text = await format_student_topics_stats_real(
        student.id,
        int(subject_id),
        "detailed"
    )

    await callback.message.edit_text(
        progress_text,
        reply_markup=get_back_to_progress_kb()
    )
    await state.set_state(ProgressStates.subject_details)