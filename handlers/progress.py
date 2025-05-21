from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from keyboards.progress import get_progress_menu_kb, get_subjects_progress_kb, get_back_to_progress_kb

router = Router()

class ProgressStates(StatesGroup):
    main = State()
    subjects = State()
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
    
    # Определяем название предмета
    subject_name = "Химия"  # В реальном приложении это будет определяться по subject_id
    
    # Пример данных о прогрессе (в реальном приложении будут загружаться из БД)
    topics_progress = {
        "Алканы": 90,
        "Изомерия": 33,
        "Кислоты": 60,
        "Циклоалканы": None  # None означает, что тема не проверена
    }
    
    # Формируем текст с прогрессом
    progress_text = f"📗 Прогресс по {subject_name}\n"
    
    # Добавляем информацию о каждой теме
    for topic, percentage in topics_progress.items():
        if percentage is None:
            progress_text += f"• {topic} — ❌ Не проверено\n"
        else:
            progress_text += f"• {topic} — {percentage}%\n"
    
    # Определяем сильные и слабые темы
    strong_topics = [topic for topic, percentage in topics_progress.items() 
                    if percentage is not None and percentage >= 80]
    weak_topics = [topic for topic, percentage in topics_progress.items() 
                  if percentage is not None and percentage <= 40]
    
    # Добавляем информацию о сильных и слабых темах
    if strong_topics:
        progress_text += "\n🟢 Сильные темы (≥80%):\n"
        for topic in strong_topics:
            progress_text += f"• {topic}\n"
    
    if weak_topics:
        progress_text += "\n🔴 Слабые темы (≤40%):\n"
        for topic in weak_topics:
            progress_text += f"• {topic}\n"
    
    await callback.message.edit_text(
        progress_text,
        reply_markup=get_back_to_progress_kb()
    )
    await state.set_state(ProgressStates.subject_details)

@router.callback_query(F.data == "back_to_progress")
async def back_to_progress_menu(callback: CallbackQuery, state: FSMContext):
    """Вернуться в меню прогресса"""
    await show_progress_menu(callback, state)