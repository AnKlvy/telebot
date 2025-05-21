from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from keyboards import get_main_menu_kb, get_courses_kb, get_subjects_kb, get_lessons_kb, get_homeworks_kb, \
    get_confirm_kb

router = Router()

class HomeworkStates(StatesGroup):
    course = State()
    subject = State()
    lesson = State()
    homework = State()
    confirmation = State()

@router.message(CommandStart())
async def main_menu_command(message: Message):
    await show_main_menu(message)

@router.message(F.text.func(lambda text: text.lower() == "меню"))
async def main_menu_text(message: Message):
    await show_main_menu(message)

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


@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await show_main_menu(callback.message)
    await state.clear()

@router.callback_query(F.data == "back_to_course")
async def back_to_course(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "Выбери курс, по которому хочешь пройти домашнее задание 👇",
        reply_markup=get_courses_kb()
    )
    await state.set_state(HomeworkStates.course)

@router.callback_query(F.data == "back_to_subject")
async def back_to_subject(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "Теперь выбери предмет — это поможет выбрать нужные темы и задания 📚",
        reply_markup=get_subjects_kb()
    )
    await state.set_state(HomeworkStates.subject)

# Словарь переходов между состояниями
STATE_TRANSITIONS = {
    HomeworkStates.confirmation: HomeworkStates.homework,
    HomeworkStates.homework: HomeworkStates.lesson,
    HomeworkStates.lesson: HomeworkStates.subject,
    HomeworkStates.subject: HomeworkStates.course,
    HomeworkStates.course: None  # None означает возврат в главное меню
}

# Словарь обработчиков для каждого состояния
STATE_HANDLERS = {
    HomeworkStates.course: choose_course,
    HomeworkStates.subject: choose_subject,
    HomeworkStates.lesson: choose_lesson,
    # Добавьте остальные обработчики по мере необходимости
}

@router.callback_query(F.data == "back")
async def go_back(callback: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    
    if not current_state or current_state not in STATE_TRANSITIONS:
        # Если текущего состояния нет или оно не в словаре переходов, возвращаемся в главное меню
        await callback.message.delete()
        await show_main_menu(callback.message)
        await state.clear()
        return
    
    # Получаем предыдущее состояние из словаря переходов
    prev_state = STATE_TRANSITIONS[current_state]
    
    if prev_state is None:
        # Если предыдущее состояние None, возвращаемся в главное меню
        await callback.message.delete()
        await show_main_menu(callback.message)
        await state.clear()
        return
    
    # Вызываем соответствующий обработчик для предыдущего состояния
    if prev_state in STATE_HANDLERS:
        await STATE_HANDLERS[prev_state](callback, state)
    else:
        # Если обработчик не найден, возвращаемся в главное меню
        await callback.message.delete()
        await show_main_menu(callback.message)
        await state.clear()