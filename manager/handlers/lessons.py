from aiogram import Router, F, types
from aiogram.types import CallbackQuery, Message
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from manager.keyboards.lessons import (
    get_lessons_menu_kb,
    get_courses_list_kb,
    get_subjects_list_kb,
    get_lessons_list_kb,
    confirm_delete_lesson_kb,
    LessonCallback,
    LessonActions
)

router = Router()

# Временное хранилище данных (потом заменить на БД)
courses_db = {
    1: "ЕНТ",
    2: "IT"
}

subjects_db = {
    1: ["Математика", "Физика", "Информатика"],
    2: ["Python", "JavaScript", "Java"]
}

lessons_db = {
    "Математика": ["Тригонометрия", "Планиметрия", "Стереометрия"],
    "Физика": ["Механика", "Оптика", "Электричество"],
    "Информатика": ["Алгоритмы", "Массивы", "Циклы"],
    "Python": ["Основы", "ООП", "Flask"],
    "JavaScript": ["DOM", "React", "Node.js"],
    "Java": ["Core", "Spring", "Android"]
}

class ManagerLessonStates(StatesGroup):
    main = State()  # Главное меню уроков (выбор курса)
    select_subject = State()  # Выбор предмета
    lessons_list = State()  # Список уроков предмета
    adding_lesson = State()  # Добавление нового урока
    confirm_deletion = State()  # Подтверждение удаления

@router.callback_query(F.data == "manager_lessons")
async def show_courses(callback: CallbackQuery, state: FSMContext):
    """Показываем список курсов"""
    await callback.message.edit_text(
        text="Выберите курс для работы с уроками:",
        reply_markup=get_courses_list_kb(courses_db)
    )
    await state.set_state(ManagerLessonStates.main)

@router.callback_query(LessonCallback.filter(F.action == LessonActions.VIEW))
async def process_view_action(callback: CallbackQuery, callback_data: LessonCallback, state: FSMContext):
    """Обработка просмотра списков"""
    if callback_data.course_id is not None and callback_data.subject_id is None:
        # Показываем список предметов для курса
        subjects = subjects_db.get(callback_data.course_id, [])
        await state.update_data(course_id=callback_data.course_id)
        await state.set_state(ManagerLessonStates.select_subject)
        await callback.message.edit_text(
            text=f"Выберите предмет из курса {courses_db[callback_data.course_id]}:",
            reply_markup=get_subjects_list_kb(subjects, callback_data.course_id)
        )
    elif callback_data.subject_id is not None:
        # Показываем список уроков для предмета
        subject_name = subjects_db[callback_data.course_id][callback_data.subject_id]
        lessons = lessons_db.get(subject_name, [])
        await state.update_data(
            subject_id=callback_data.subject_id,
            subject_name=subject_name
        )
        await state.set_state(ManagerLessonStates.lessons_list)
        await callback.message.edit_text(
            text=f"📝 Список уроков по предмету {subject_name}:\n"
                 f"Всего уроков: {len(lessons)}",
            reply_markup=get_lessons_list_kb(
                lessons,
                course_id=callback_data.course_id,
                subject_id=callback_data.subject_id
            )
        )

@router.callback_query(LessonCallback.filter(F.action == LessonActions.ADD))
async def start_add_lesson(callback: CallbackQuery, callback_data: LessonCallback, state: FSMContext):
    """Начинаем процесс добавления урока"""
    data = await state.get_data()
    subject_name = data.get('subject_name')
    
    await state.set_state(ManagerLessonStates.adding_lesson)
    await callback.message.edit_text(
        text=f"Введите название нового урока для предмета {subject_name}:",
        reply_markup=get_home_kb()
    )

@router.message(StateFilter(ManagerLessonStates.adding_lesson))
async def process_lesson_name(message: Message, state: FSMContext):
    """Обрабатываем ввод названия урока"""
    data = await state.get_data()
    subject_name = data['subject_name']
    new_lesson_name = message.text.strip()
    
    if subject_name not in lessons_db:
        lessons_db[subject_name] = []
    lessons_db[subject_name].append(new_lesson_name)
    
    await state.set_state(ManagerLessonStates.lessons_list)
    await message.answer(
        text=f"✅ Урок \"{new_lesson_name}\" успешно добавлен в предмет {subject_name}\n"
             f"Всего уроков: {len(lessons_db[subject_name])}",
        reply_markup=get_lessons_list_kb(
            lessons_db[subject_name],
            course_id=data['course_id'],
            subject_id=data['subject_id']
        )
    )

@router.callback_query(LessonCallback.filter(F.action == LessonActions.DELETE))
async def confirm_delete(callback: CallbackQuery, callback_data: LessonCallback, state: FSMContext):
    """Запрашиваем подтверждение удаления урока"""
    data = await state.get_data()
    subject_name = data['subject_name']
    lesson_to_delete = lessons_db[subject_name][callback_data.lesson_id]
    
    await state.set_state(ManagerLessonStates.confirm_deletion)
    await callback.message.edit_text(
        text=f"❗️ Вы уверены, что хотите удалить урок \"{lesson_to_delete}\" из предмета {subject_name}?",
        reply_markup=confirm_delete_lesson_kb(callback_data.lesson_id)
    )

@router.callback_query(LessonCallback.filter(F.action == LessonActions.CONFIRM_DELETE))
async def process_delete_lesson(callback: CallbackQuery, callback_data: LessonCallback, state: FSMContext):
    """Удаляем урок после подтверждения"""
    data = await state.get_data()
    subject_name = data['subject_name']
    lesson_to_delete = lessons_db[subject_name].pop(callback_data.lesson_id)
    
    await state.set_state(ManagerLessonStates.lessons_list)
    await callback.message.edit_text(
        text=f"✅ Урок \"{lesson_to_delete}\" успешно удален из предмета {subject_name}\n"
             f"Всего уроков: {len(lessons_db[subject_name])}",
        reply_markup=get_lessons_list_kb(
            lessons_db[subject_name],
            course_id=data['course_id'],
            subject_id=data['subject_id']
        )
    )

@router.callback_query(LessonCallback.filter(F.action == LessonActions.CANCEL))
async def cancel_action(callback: CallbackQuery, callback_data: LessonCallback, state: FSMContext):
    """Отмена действия"""
    data = await state.get_data()
    subject_name = data['subject_name']
    
    await state.set_state(ManagerLessonStates.lessons_list)
    await callback.message.edit_text(
        text=f"📝 Список уроков по предмету {subject_name}:\n"
             f"Всего уроков: {len(lessons_db[subject_name])}",
        reply_markup=get_lessons_list_kb(
            lessons_db[subject_name],
            course_id=data['course_id'],
            subject_id=data['subject_id']
        )
    )