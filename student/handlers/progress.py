from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from ..keyboards.progress import get_progress_menu_kb, get_subjects_progress_kb, get_back_to_progress_kb
# Импорты статистики перенесены в обработчики

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
    from database import StudentRepository

    # Получаем студента по Telegram ID
    student = await StudentRepository.get_by_telegram_id(callback.from_user.id)

    if not student:
        await callback.message.edit_text(
            "❌ Студент не найден в системе",
            reply_markup=get_back_to_progress_kb()
        )
        return

    # Получаем общую статистику студента
    general_stats = await StudentRepository.get_general_stats(student.id)

    await callback.message.edit_text(
        f"Вот твоя краткая статистика 👇\n"
        f"📊 Баллы: {general_stats.get('total_points', 0)}\n"
        f"🎯 Уровень: {student.level}\n"
        f"📋 Выполнено домашних заданий: {general_stats.get('total_completed', 0)}",
        reply_markup=get_back_to_progress_kb()
    )
    await state.set_state(ProgressStates.common_stats)

@router.callback_query(ProgressStates.main, F.data == "topics_understanding")
async def show_subjects_list(callback: CallbackQuery, state: FSMContext):
    """Показать список предметов для просмотра понимания по темам"""
    await callback.message.edit_text(
        "Выбери предмет, чтобы посмотреть % понимания по микротемам:",
        reply_markup=await get_subjects_progress_kb()
    )
    await state.set_state(ProgressStates.subjects)

@router.callback_query(ProgressStates.subjects, F.data.startswith("progress_sub_"))
async def show_subject_progress(callback: CallbackQuery, state: FSMContext):
    """Показать кнопки выбора типа статистики по предмету"""
    subject_id = callback.data.replace("progress_sub_", "")

    # Получаем ID студента из Telegram ID
    from database import StudentRepository, SubjectRepository
    student = await StudentRepository.get_by_telegram_id(callback.from_user.id)

    if not student:
        await callback.message.edit_text(
            "❌ Студент не найден в системе",
            reply_markup=get_back_to_progress_kb()
        )
        return

    # Получаем название предмета
    subject = await SubjectRepository.get_by_id(int(subject_id))
    subject_name = subject.name if subject else "Предмет"

    # Показываем кнопки выбора типа статистики
    from common.analytics.keyboards import get_student_microtopics_kb

    await callback.message.edit_text(
        f"📊 Выбери тип статистики по предмету {subject_name}:",
        reply_markup=get_student_microtopics_kb(student.id, int(subject_id))
    )
    await state.set_state(ProgressStates.subject_details)

# Добавляем обработчики для кнопок статистики
@router.callback_query(ProgressStates.subject_details, F.data.startswith("microtopics_detailed_"))
async def show_detailed_microtopics(callback: CallbackQuery, state: FSMContext):
    """Показать детальную статистику по микротемам"""
    from common.statistics import get_student_microtopics_detailed

    # Извлекаем student_id и subject_id из callback_data
    parts = callback.data.split("_")
    if len(parts) >= 4:
        student_id = int(parts[2])
        subject_id = int(parts[3])

        # Получаем детальную статистику
        result_text = await get_student_microtopics_detailed(student_id, subject_id)

        await callback.message.edit_text(
            result_text,
            reply_markup=get_back_to_progress_kb()
        )
    else:
        await callback.message.edit_text(
            "❌ Ошибка в данных запроса",
            reply_markup=get_back_to_progress_kb()
        )

@router.callback_query(ProgressStates.subject_details, F.data.startswith("microtopics_summary_"))
async def show_summary_microtopics(callback: CallbackQuery, state: FSMContext):
    """Показать сводку по сильным и слабым темам"""
    from common.statistics import get_student_strong_weak_summary

    # Извлекаем student_id и subject_id из callback_data
    parts = callback.data.split("_")
    if len(parts) >= 4:
        student_id = int(parts[2])
        subject_id = int(parts[3])

        # Получаем сводку по сильным и слабым темам
        result_text = await get_student_strong_weak_summary(student_id, subject_id)

        await callback.message.edit_text(
            result_text,
            reply_markup=get_back_to_progress_kb()
        )
    else:
        await callback.message.edit_text(
            "❌ Ошибка в данных запроса",
            reply_markup=get_back_to_progress_kb()
        )