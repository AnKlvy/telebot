from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from ..keyboards.homework import (
    get_main_menu_kb, get_courses_kb, get_subjects_kb, get_lessons_kb,
    get_homeworks_kb, get_confirm_kb, get_test_answers_kb, get_after_test_kb
)
from .test_logic import start_test_process, process_test_answer
from aiogram.fsm.state import State, StatesGroup

class HomeworkStates(StatesGroup):
    course = State()
    subject = State()
    lesson = State()
    homework = State()
    confirmation = State()
    test_in_progress = State()

router = Router()

async def show_main_menu(message: Message):
    await message.answer(
        "Привет 👋\n"
        "Здесь ты можешь проходить домашки, прокачивать темы, отслеживать свой прогресс и готовиться к ЕНТ.\n"
        "Ниже — все разделы, которые тебе доступны:",
        reply_markup=get_main_menu_kb()
    )

@router.callback_query(F.data == "homework")
async def choose_course(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "Выбери курс, по которому хочешь пройти домашнее задание 👇",
        reply_markup=get_courses_kb()
    )
    await state.set_state(HomeworkStates.course)

@router.callback_query(HomeworkStates.course, F.data.startswith("course_"))
async def choose_subject(callback: CallbackQuery, state: FSMContext):
    await state.update_data(course=callback.data)
    await callback.message.edit_text(
        "Теперь выбери предмет — это поможет выбрать нужные темы и задания 📚",
        reply_markup=get_subjects_kb()
    )
    await state.set_state(HomeworkStates.subject)

@router.callback_query(HomeworkStates.subject, F.data.startswith("sub_"))
async def choose_lesson(callback: CallbackQuery, state: FSMContext):
    await state.update_data(subject=callback.data)
    await callback.message.edit_text(
        "Выбери урок, по которому хочешь пройти домашнее задание👇",
        reply_markup=get_lessons_kb()
    )
    await state.set_state(HomeworkStates.lesson)

@router.callback_query(HomeworkStates.lesson, F.data.startswith("lesson_"))
async def choose_homework(callback: CallbackQuery, state: FSMContext):
    lesson_id = callback.data.replace("lesson_", "")
    lesson_name = ""
    if lesson_id == "alkanes":
        lesson_name = "Алканы"
    elif lesson_id == "isomeria":
        lesson_name = "Изомерия"
    elif lesson_id == "acids":
        lesson_name = "Кислоты"

    await state.update_data(lesson=callback.data, lesson_name=lesson_name)
    await callback.message.edit_text(
        "Вот доступные домашние задания по этой теме👇",
        reply_markup=get_homeworks_kb()
    )
    await state.set_state(HomeworkStates.homework)

@router.callback_query(HomeworkStates.homework, F.data.startswith("homework_"))
async def confirm_homework(callback: CallbackQuery, state: FSMContext):
    homework_type = callback.data.replace("homework_", "")
    homework_name = ""
    if homework_type == "basic":
        homework_name = "Базовое"
    elif homework_type == "advanced":
        homework_name = "Углублённое"
    elif homework_type == "review":
        homework_name = "Повторение"

    await state.update_data(homework=callback.data, homework_name=homework_name)

    # Получаем данные о выбранном уроке
    user_data = await state.get_data()
    lesson_name = user_data.get("lesson_name", "")

    await callback.message.edit_text(
        f"🔎 Урок: {lesson_name}\n"
        f"📋 Вопросов: 15\n"
        f"⏱ Время на прохождение одного вопроса: 10 секунд\n"
        f"⚠️ Баллы будут начислены только за 100% правильных ответов.\n"
        f"Ты готов?",
        reply_markup=get_confirm_kb()
    )
    await state.set_state(HomeworkStates.confirmation)

@router.callback_query(HomeworkStates.confirmation, F.data == "start_test")
async def start_test(callback: CallbackQuery, state: FSMContext):
    await start_test_process(callback, state)
    await state.set_state(HomeworkStates.test_in_progress)

@router.callback_query(F.data == "back_to_main_menu")
async def back_to_main_menu(callback: CallbackQuery, state: FSMContext):
    """Возврат в главное меню"""
    await callback.message.delete()
    await show_main_menu(callback.message)
    await state.clear()

# Обработчик ответов на вопросы теста
@router.callback_query(HomeworkStates.test_in_progress, F.data.startswith("answer_"))
async def process_answer(callback: CallbackQuery, state: FSMContext):
    selected_answer = callback.data.replace("answer_", "")
    await process_test_answer(callback, state, selected_answer)

@router.callback_query(F.data == "retry_test")
async def retry_test(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "Вот доступные домашние задания по этой теме👇",
        reply_markup=get_homeworks_kb()
    )
    await state.set_state(HomeworkStates.homework)
