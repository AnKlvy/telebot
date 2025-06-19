from aiogram import Router, F, types
from aiogram.types import CallbackQuery, Message
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import logging

from manager.keyboards.lessons import (
    get_lessons_menu_kb,
    get_courses_list_kb,
    get_subjects_list_kb,
    get_lessons_list_kb,
    confirm_delete_lesson_kb,
    LessonCallback,
    LessonActions
)
from common.keyboards import get_home_kb
from database.repositories.lesson_repository import LessonRepository
from database.repositories.subject_repository import SubjectRepository
from database.repositories.course_repository import CourseRepository

# Настройка логирования
logger = logging.getLogger(__name__)

router = Router()

class ManagerLessonStates(StatesGroup):
    main = State()  # Главное меню уроков (выбор курса)
    select_subject = State()  # Выбор предмета
    lessons_list = State()  # Список уроков предмета
    adding_lesson = State()  # Добавление нового урока
    confirm_deletion = State()  # Подтверждение удаления

@router.callback_query(F.data == "manager_lessons")
async def show_courses(callback: CallbackQuery, state: FSMContext):
    """Показываем список курсов"""
    # Получаем список курсов из БД
    courses = await CourseRepository.get_all()
    
    await callback.message.edit_text(
        text="Выберите курс для работы с уроками:",
        reply_markup=await get_courses_list_kb(courses)
    )
    await state.set_state(ManagerLessonStates.main)

@router.callback_query(LessonCallback.filter(F.action == LessonActions.VIEW), StateFilter(ManagerLessonStates.main, ManagerLessonStates.select_subject))
async def process_view_action(callback: CallbackQuery, callback_data: LessonCallback, state: FSMContext):
    """Обработка просмотра списков"""
    # Получаем course_id и subject_id из callback_data или состояния
    course_id = None
    subject_id = None

    if hasattr(callback_data, 'course_id') and callback_data.course_id is not None:
        course_id = callback_data.course_id
    else:
        # Если callback_data не содержит course_id, берем из состояния
        user_data = await state.get_data()
        course_id = user_data.get('course_id')

    if hasattr(callback_data, 'subject_id') and callback_data.subject_id is not None:
        subject_id = callback_data.subject_id
    else:
        # Если callback_data не содержит subject_id, берем из состояния
        user_data = await state.get_data()
        subject_id = user_data.get('subject_id')

    if course_id is not None and subject_id is None:
        # Показываем список предметов для курса
        course = await CourseRepository.get_by_id(course_id)
        if not course:
            await callback.message.edit_text(
                text="❌ Курс не найден!",
                reply_markup=get_home_kb()
            )
            return
            
        # Получаем предметы для курса
        subjects = await SubjectRepository.get_by_course(course_id)

        # Очищаем данные о предмете при выборе нового курса
        await state.update_data(course_id=course_id, course_name=course.name, subject_id=None, subject_name=None)
        await state.set_state(ManagerLessonStates.select_subject)
        await callback.message.edit_text(
            text=f"Выберите предмет из курса {course.name}:",
            reply_markup=await get_subjects_list_kb(subjects, course_id)
        )
    elif subject_id is not None:
        # Показываем список уроков для предмета
        subject = await SubjectRepository.get_by_id(subject_id)
        if not subject:
            await callback.message.edit_text(
                text="❌ Предмет не найден!",
                reply_markup=get_home_kb()
            )
            return
            
        # Получаем уроки для предмета и курса
        lessons = await LessonRepository.get_by_subject_and_course(subject_id, course_id)
        
        await state.update_data(
            subject_id=subject_id,
            subject_name=subject.name
        )
        await state.set_state(ManagerLessonStates.lessons_list)
        await callback.message.edit_text(
            text=f"📝 Список уроков по предмету {subject.name}:\n"
                 f"Всего уроков: {len(lessons)}",
            reply_markup=await get_lessons_list_kb(
                lessons,
                course_id=course_id,
                subject_id=subject_id
            )
        )

# Отдельные обработчики для навигации назад
async def back_to_select_subject(callback: CallbackQuery, state: FSMContext):
    """Обработчик для возврата к выбору предмета"""
    user_data = await state.get_data()
    course_id = user_data.get('course_id')
    course_name = user_data.get('course_name')

    if course_id:
        # Получаем предметы для курса
        subjects = await SubjectRepository.get_by_course(course_id)

        # Очищаем данные о предмете при возврате к выбору предмета
        await state.update_data(subject_id=None, subject_name=None)
        await state.set_state(ManagerLessonStates.select_subject)
        await callback.message.edit_text(
            text=f"Выберите предмет из курса {course_name}:",
            reply_markup=await get_subjects_list_kb(subjects, course_id)
        )

async def back_to_lessons_list(callback: CallbackQuery, state: FSMContext):
    """Обработчик для возврата к списку уроков"""
    user_data = await state.get_data()
    course_id = user_data.get('course_id')
    subject_id = user_data.get('subject_id')
    subject_name = user_data.get('subject_name')

    if course_id and subject_id and subject_name:
        # Получаем уроки для предмета
        lessons = await LessonRepository.get_by_subject(subject_id)
        
        await state.set_state(ManagerLessonStates.lessons_list)
        await callback.message.edit_text(
            text=f"📝 Список уроков по предмету {subject_name}:\n"
                 f"Всего уроков: {len(lessons)}",
            reply_markup=await get_lessons_list_kb(
                lessons,
                course_id=course_id,
                subject_id=subject_id
            )
        )

@router.callback_query(LessonCallback.filter(F.action == LessonActions.ADD), StateFilter(ManagerLessonStates.lessons_list))
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
    subject_id = data['subject_id']
    subject_name = data['subject_name']
    new_lesson_name = message.text.strip()
    
    try:
        # Создаем урок в базе данных
        lesson = await LessonRepository.create(new_lesson_name, subject_id, data['course_id'])

        # Получаем обновленный список уроков
        lessons = await LessonRepository.get_by_subject_and_course(subject_id, data['course_id'])
        
        await state.set_state(ManagerLessonStates.lessons_list)
        await message.answer(
            text=f"✅ Урок \"{new_lesson_name}\" успешно добавлен в предмет {subject_name}\n"
                 f"Всего уроков: {len(lessons)}",
            reply_markup=await get_lessons_list_kb(
                lessons,
                course_id=data['course_id'],
                subject_id=subject_id
            )
        )
    except ValueError as e:
        # Урок уже существует или другая ошибка
        await message.answer(
            text=f"❌ {str(e)}\n\nВведите другое название:",
            reply_markup=get_home_kb()
        )

@router.callback_query(LessonCallback.filter(F.action == LessonActions.DELETE), StateFilter(ManagerLessonStates.lessons_list))
async def confirm_delete(callback: CallbackQuery, callback_data: LessonCallback, state: FSMContext):
    """Запрашиваем подтверждение удаления урока"""
    lesson_id = callback_data.lesson_id
    
    # Получаем информацию об уроке
    lesson = await LessonRepository.get_by_id(lesson_id)
    if not lesson:
        await callback.message.edit_text(
            text="❌ Урок не найден!",
            reply_markup=get_home_kb()
        )
        return
    
    data = await state.get_data()
    subject_name = data['subject_name']
    
    # Сохраняем данные для удаления
    await state.update_data(lesson_id=lesson_id, lesson_name=lesson.name)
    
    await state.set_state(ManagerLessonStates.confirm_deletion)
    await callback.message.edit_text(
        text=f"❗️ Вы уверены, что хотите удалить урок \"{lesson.name}\" из предмета {subject_name}?",
        reply_markup=confirm_delete_lesson_kb(lesson_id)
    )

@router.callback_query(LessonCallback.filter(F.action == LessonActions.CONFIRM_DELETE), StateFilter(ManagerLessonStates.confirm_deletion))
async def process_delete_lesson(callback: CallbackQuery, callback_data: LessonCallback, state: FSMContext):
    """Удаляем урок после подтверждения"""
    data = await state.get_data()
    lesson_id = data['lesson_id']
    lesson_name = data['lesson_name']
    subject_id = data['subject_id']
    subject_name = data['subject_name']
    
    # Удаляем урок из базы данных
    success = await LessonRepository.delete(lesson_id)
    
    if success:
        # Получаем обновленный список уроков
        lessons = await LessonRepository.get_by_subject_and_course(subject_id, data['course_id'])
        
        await state.set_state(ManagerLessonStates.lessons_list)
        await callback.message.edit_text(
            text=f"✅ Урок \"{lesson_name}\" успешно удален из предмета {subject_name}\n"
                 f"Всего уроков: {len(lessons)}",
            reply_markup=await get_lessons_list_kb(
                lessons,
                course_id=data['course_id'],
                subject_id=subject_id
            )
        )
    else:
        await callback.message.edit_text(
            text=f"❌ Ошибка при удалении урока \"{lesson_name}\"",
            reply_markup=get_home_kb()
        )

@router.callback_query(LessonCallback.filter(F.action == LessonActions.CANCEL), StateFilter(ManagerLessonStates.confirm_deletion))
async def cancel_action(callback: CallbackQuery, callback_data: LessonCallback, state: FSMContext):
    """Отмена действия"""
    await back_to_lessons_list(callback, state)