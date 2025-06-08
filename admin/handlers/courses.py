from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter

from admin.utils.common import (
    add_course, remove_course,
    get_subjects_list_kb, get_courses_list_kb, get_confirmation_kb
)
from common.keyboards import back_to_main_button, get_home_kb

router = Router()

class AdminCoursesStates(StatesGroup):
    # Состояния для добавления курса
    enter_course_name = State()
    select_course_subjects = State()
    confirm_add_course = State()
    
    # Состояния для удаления курса
    select_course_to_delete = State()
    confirm_delete_course = State()

# === ДОБАВЛЕНИЕ КУРСА ===

@router.callback_query(F.data == "add_course")
async def start_add_course(callback: CallbackQuery, state: FSMContext):
    """Начать добавление курса"""
    await callback.message.edit_text(
        text="Введите название курса:",
        reply_markup=get_home_kb()
    )
    await state.set_state(AdminCoursesStates.enter_course_name)

@router.message(StateFilter(AdminCoursesStates.enter_course_name))
async def process_course_name(message: Message, state: FSMContext):
    """Обработать ввод названия курса"""
    course_name = message.text.strip()
    
    await state.update_data(course_name=course_name, selected_subject_ids=[])
    await state.set_state(AdminCoursesStates.select_course_subjects)

    await message.answer(
        text=f"Курс: {course_name}\n\n"
             f"Выберите предметы для курса (можно выбрать несколько):\n"
             f"Выбрано: 0",
        reply_markup=await get_subjects_selection_kb([])
    )

async def get_subjects_selection_kb(selected_subject_ids: list):
    """Клавиатура для выбора предметов с возможностью множественного выбора"""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    from database import SubjectRepository

    buttons = []

    # Получаем все предметы из базы данных
    all_subjects = await SubjectRepository.get_all()

    for subject in all_subjects:
        if subject.id in selected_subject_ids:
            # Предмет уже выбран
            buttons.append([
                InlineKeyboardButton(
                    text=f"✅ {subject.name}",
                    callback_data=f"unselect_subject_{subject.id}"
                )
            ])
        else:
            # Предмет не выбран
            buttons.append([
                InlineKeyboardButton(
                    text=f"⬜ {subject.name}",
                    callback_data=f"select_subject_{subject.id}"
                )
            ])

    # Кнопки управления
    if selected_subject_ids:
        buttons.append([
            InlineKeyboardButton(text="✅ Готово", callback_data="finish_subject_selection")
        ])

    buttons.extend([
        back_to_main_button()
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

@router.callback_query(AdminCoursesStates.select_course_subjects, F.data.startswith("select_subject_"))
async def select_subject_for_course(callback: CallbackQuery, state: FSMContext):
    """Выбрать предмет для курса"""
    subject_id = int(callback.data.replace("select_subject_", ""))
    data = await state.get_data()

    selected_subject_ids = data.get("selected_subject_ids", [])
    if subject_id not in selected_subject_ids:
        selected_subject_ids.append(subject_id)

    await state.update_data(selected_subject_ids=selected_subject_ids)

    course_name = data.get("course_name", "")
    await callback.message.edit_text(
        text=f"Курс: {course_name}\n\n"
             f"Выберите предметы для курса (можно выбрать несколько):\n"
             f"Выбрано: {len(selected_subject_ids)}",
        reply_markup=await get_subjects_selection_kb(selected_subject_ids)
    )

@router.callback_query(AdminCoursesStates.select_course_subjects, F.data.startswith("unselect_subject_"))
async def unselect_subject_for_course(callback: CallbackQuery, state: FSMContext):
    """Отменить выбор предмета для курса"""
    subject_id = int(callback.data.replace("unselect_subject_", ""))
    data = await state.get_data()

    selected_subject_ids = data.get("selected_subject_ids", [])
    if subject_id in selected_subject_ids:
        selected_subject_ids.remove(subject_id)

    await state.update_data(selected_subject_ids=selected_subject_ids)

    course_name = data.get("course_name", "")
    await callback.message.edit_text(
        text=f"Курс: {course_name}\n\n"
             f"Выберите предметы для курса (можно выбрать несколько):\n"
             f"Выбрано: {len(selected_subject_ids)}",
        reply_markup=await get_subjects_selection_kb(selected_subject_ids)
    )

@router.callback_query(AdminCoursesStates.select_course_subjects, F.data == "finish_subject_selection")
async def finish_subject_selection(callback: CallbackQuery, state: FSMContext):
    """Завершить выбор предметов"""
    from database import SubjectRepository

    data = await state.get_data()
    course_name = data.get("course_name", "")
    selected_subject_ids = data.get("selected_subject_ids", [])

    # Получаем названия предметов по ID
    subjects_names = []
    for subject_id in selected_subject_ids:
        subject = await SubjectRepository.get_by_id(subject_id)
        if subject:
            subjects_names.append(subject.name)

    subjects_text = "\n".join([f"• {name}" for name in subjects_names])

    await state.set_state(AdminCoursesStates.confirm_add_course)
    await callback.message.edit_text(
        text=f"📋 Подтверждение создания курса:\n\n"
             f"Название: {course_name}\n"
             f"Предметы ({len(selected_subject_ids)}):\n{subjects_text}",
        reply_markup=get_confirmation_kb("add", "course")
    )

@router.callback_query(AdminCoursesStates.confirm_add_course, F.data.startswith("confirm_add_course"))
async def confirm_add_course(callback: CallbackQuery, state: FSMContext):
    """Подтвердить добавление курса"""
    data = await state.get_data()
    course_name = data.get("course_name", "")
    selected_subject_ids = data.get("selected_subject_ids", [])

    course_id = await add_course(course_name, selected_subject_ids)

    await callback.message.edit_text(
        text=f"✅ Курс '{course_name}' успешно создан!\n"
             f"ID курса: {course_id}",
        reply_markup=get_home_kb()
    )
    await state.clear()

# === УДАЛЕНИЕ КУРСА ===

@router.callback_query(F.data == "remove_course")
async def start_remove_course(callback: CallbackQuery, state: FSMContext):
    """Начать удаление курса"""
    await callback.message.edit_text(
        text="Выберите курс для удаления:",
        reply_markup=await get_courses_list_kb("delete_course")
    )
    await state.set_state(AdminCoursesStates.select_course_to_delete)

@router.callback_query(AdminCoursesStates.select_course_to_delete, F.data.startswith("delete_course_"))
async def select_course_to_delete(callback: CallbackQuery, state: FSMContext):
    """Выбрать курс для удаления"""
    from database import CourseRepository, SubjectRepository

    course_id = int(callback.data.replace("delete_course_", ""))
    course = await CourseRepository.get_by_id(course_id)

    if not course:
        await callback.message.edit_text(
            text="❌ Курс не найден!",
            reply_markup=get_home_kb()
        )
        return

    # Получаем предметы курса
    subjects = await SubjectRepository.get_by_course(course_id)
    subjects_text = "\n".join([f"• {subject.name}" for subject in subjects])

    await state.update_data(course_to_delete=course_id, course_name=course.name)
    await state.set_state(AdminCoursesStates.confirm_delete_course)

    await callback.message.edit_text(
        text=f"🗑 Подтверждение удаления курса:\n\n"
             f"Название: {course.name}\n"
             f"Предметы:\n{subjects_text}\n\n"
             f"⚠️ Это действие нельзя отменить!",
        reply_markup=get_confirmation_kb("delete", "course", str(course_id))
    )

@router.callback_query(AdminCoursesStates.confirm_delete_course, F.data.startswith("confirm_delete_course"))
async def confirm_delete_course(callback: CallbackQuery, state: FSMContext):
    """Подтвердить удаление курса"""
    data = await state.get_data()
    course_id = data.get("course_to_delete")
    course_name = data.get("course_name", "Неизвестный курс")

    success = await remove_course(course_id)

    if success:
        await callback.message.edit_text(
            text=f"✅ Курс '{course_name}' успешно удален!",
            reply_markup=get_home_kb()
        )
    else:
        await callback.message.edit_text(
            text=f"❌ Курс '{course_name}' не найден!",
            reply_markup=get_home_kb()
        )

    await state.clear()

# === ОТМЕНА ДЕЙСТВИЙ ===

@router.callback_query(F.data.startswith("cancel_add_course") | F.data.startswith("cancel_delete_course"))
async def cancel_course_action(callback: CallbackQuery, state: FSMContext):
    """Отменить действие с курсом"""
    await callback.message.edit_text(
        text="❌ Действие отменено",
        reply_markup=get_home_kb()
    )
    await state.clear()
