from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from common.utils import check_if_id_in_callback_data
from ..keyboards.homework import get_courses_kb, get_subjects_kb, get_lessons_kb
from aiogram.fsm.state import State, StatesGroup
from database import HomeworkRepository, LessonRepository, SubjectRepository, CourseRepository
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from common.keyboards import get_main_menu_back_button

class HomeworkStates(StatesGroup):
    course = State()
    subject = State()
    lesson = State()
    homework = State()
    confirmation = State()
    test_in_progress = State()
    repeat_test = State()

router = Router()


@router.callback_query(F.data == "homework")
async def choose_course(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "Выбери курс, по которому хочешь пройти домашнее задание 👇",
        reply_markup=await get_courses_kb(user_id=callback.from_user.id)
    )
    await state.set_state(HomeworkStates.course)

@router.callback_query(HomeworkStates.course, F.data == "no_courses")
async def handle_no_courses(callback: CallbackQuery, state: FSMContext):
    """Обработчик для случая когда у студента нет доступных курсов"""
    await callback.message.edit_text(
        "📚 У вас пока нет доступных курсов\n\n"
        "Обратитесь к администратору или куратору для добавления вас в курсы.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            *get_main_menu_back_button()
        ])
    )

@router.callback_query(HomeworkStates.course, F.data == "courses_error")
async def handle_courses_error(callback: CallbackQuery, state: FSMContext):
    """Обработчик для случая ошибки загрузки курсов"""
    await callback.message.edit_text(
        "❌ Произошла ошибка при загрузке курсов\n\n"
        "Попробуйте позже или обратитесь к администратору.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Попробовать снова", callback_data="homework")],
            *get_main_menu_back_button()
        ])
    )

@router.callback_query(HomeworkStates.course, F.data.startswith("course_"))
async def choose_subject(callback: CallbackQuery, state: FSMContext):
    """Выбор предмета для курса"""
    course_id = int(await check_if_id_in_callback_data("course_", callback, state, "course"))

    # Получаем курс из базы данных
    course = await CourseRepository.get_by_id(course_id)
    if not course:
        await callback.answer("❌ Курс не найден", show_alert=True)
        return

    await state.update_data(course_id=course_id, course_name=course.name)

    await callback.message.edit_text(
        f"📚 Курс: {course.name}\n\n"
        "Теперь выбери предмет — это поможет выбрать нужные темы и задания:",
        reply_markup=await get_subjects_kb(course_id=course_id, user_id=callback.from_user.id)
    )
    await state.set_state(HomeworkStates.subject)

@router.callback_query(HomeworkStates.subject, F.data == "no_subjects")
async def handle_no_subjects(callback: CallbackQuery, state: FSMContext):
    """Обработчик для случая когда в курсе нет доступных предметов"""
    user_data = await state.get_data()
    course_name = user_data.get("course_name", "")

    await callback.message.edit_text(
        f"📚 Курс: {course_name}\n\n"
        "📖 В этом курсе пока нет доступных предметов\n\n"
        "Обратитесь к администратору или куратору.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            *get_main_menu_back_button()
        ])
    )

@router.callback_query(HomeworkStates.subject, F.data == "subjects_error")
async def handle_subjects_error(callback: CallbackQuery, state: FSMContext):
    """Обработчик для случая ошибки загрузки предметов"""
    user_data = await state.get_data()
    course_name = user_data.get("course_name", "")
    course_id = user_data.get("course_id")

    await callback.message.edit_text(
        f"📚 Курс: {course_name}\n\n"
        "❌ Произошла ошибка при загрузке предметов\n\n"
        "Попробуйте позже или обратитесь к администратору.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Попробовать снова", callback_data=f"course_{course_id}")],
            *get_main_menu_back_button()
        ])
    )

@router.callback_query(HomeworkStates.subject, F.data.startswith("subject_"))
async def choose_lesson(callback: CallbackQuery, state: FSMContext):
    """Выбор урока для предмета"""
    subject_id = int(await check_if_id_in_callback_data("subject_", callback, state, "subject"))

    # Получаем предмет из базы данных
    subject = await SubjectRepository.get_by_id(subject_id)
    if not subject:
        await callback.answer("❌ Предмет не найден", show_alert=True)
        return

    user_data = await state.get_data()
    course_name = user_data.get("course_name", "")
    course_id = user_data.get("course_id")

    await state.update_data(subject_id=subject.id, subject_name=subject.name)

    await callback.message.edit_text(
        f"📚 Курс: {course_name}\n"
        f"📖 Предмет: {subject.name}\n\n"
        "Выбери урок, по которому хочешь пройти домашнее задание:",
        reply_markup=await get_lessons_kb(subject.id, course_id)
    )
    await state.set_state(HomeworkStates.lesson)

@router.callback_query(HomeworkStates.lesson, F.data.startswith("lesson_"))
async def choose_homework(callback: CallbackQuery, state: FSMContext):
    """Выбор домашнего задания для урока"""
    lesson_id = int(await check_if_id_in_callback_data("lesson_", callback, state, "lesson"))

    # Получаем урок из базы данных
    lesson = await LessonRepository.get_by_id(lesson_id)
    if not lesson:
        await callback.answer("❌ Урок не найден", show_alert=True)
        return

    # Получаем домашние задания для этого урока
    homeworks = await HomeworkRepository.get_by_lesson(lesson_id)

    if not homeworks:
        user_data = await state.get_data()
        course_name = user_data.get("course_name", "")
        subject_name = user_data.get("subject_name", "")

        await callback.message.edit_text(
            f"📚 Курс: {course_name}\n"
            f"📖 Предмет: {subject_name}\n"
            f"📝 Урок: {lesson.name}\n\n"
            "❌ Для этого урока пока нет домашних заданий.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                *get_main_menu_back_button()
            ])
        )
        return

    # Получаем данные из состояния
    user_data = await state.get_data()
    course_name = user_data.get("course_name", "")
    subject_name = user_data.get("subject_name", "")

    # Сохраняем данные урока в состоянии
    await state.update_data(lesson_id=lesson_id, lesson_name=lesson.name)

    # Формируем клавиатуру с реальными домашними заданиями
    buttons = []
    for homework in homeworks:
        buttons.append([InlineKeyboardButton(
            text=homework.name,
            callback_data=f"homework_{homework.id}"
        )])

    buttons.extend(get_main_menu_back_button())

    await callback.message.edit_text(
        f"📚 Курс: {course_name}\n"
        f"📖 Предмет: {subject_name}\n"
        f"📝 Урок: {lesson.name}\n\n"
        "Выберите домашнее задание:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )
    await state.set_state(HomeworkStates.homework)

# Обработчики confirm_test, start_quiz, process_answer теперь находятся в homework_quiz.py
