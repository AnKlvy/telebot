from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
import logging
import os

from common.keyboards import get_main_menu_back_button, get_home_and_back_kb
from common.manager_tests.register_handlers import register_test_handlers
from ..keyboards.homework import (
    get_courses_kb, get_subjects_kb, get_lessons_kb,
    get_time_limit_kb, get_correct_answer_kb, get_add_question_kb,
    get_confirm_homework_kb, get_homeworks_list_kb, get_photo_skip_kb, get_homework_management_kb
)
from .main import show_manager_main_menu

from aiogram.fsm.state import State, StatesGroup

class AddHomeworkStates(StatesGroup):
    main = State()
    select_course = State()
    select_subject = State()
    select_lesson = State()
    enter_test_name = State()
    add_question = State()
    select_topic = State()
    enter_question_text = State()
    add_question_photo = State()
    enter_answer_options = State()
    select_correct_answer = State()
    set_time_limit = State()
    confirm_test = State()
    delete_test = State()
    select_test_to_delete = State()
    request_topic = State()
    process_topic = State()
    process_photo = State()
    skip_photo = State()

# Настройка логгера
logger = logging.getLogger(__name__)

router = Router()

@router.callback_query(F.data == "manager_homework")
async def show_homework_management(callback: CallbackQuery, state: FSMContext):
    """Показ меню управления домашними заданиями"""
    logger.info("Вызван обработчик show_homework_management")

    await callback.message.edit_text(
        "Управление домашними заданиями",
        reply_markup=get_homework_management_kb()
    )
    await state.set_state(AddHomeworkStates.main)
    
@router.callback_query(AddHomeworkStates.main, F.data == "manager_add_homework")
async def start_add_homework(callback: CallbackQuery, state: FSMContext):
    """Начало добавления домашнего задания"""
    logger.info("Вызван обработчик start_add_homework")

    await callback.message.edit_text(
        "Выберите курс:",
        reply_markup=get_courses_kb()
    )
    await state.set_state(AddHomeworkStates.select_course)

@router.callback_query(F.data == "manager_delete_homework")
async def start_delete_homework(callback: CallbackQuery, state: FSMContext):
    """Начало удаления домашнего задания"""
    logger.info("Вызван обработчик start_delete_homework")
    
    await callback.message.edit_text(
        "Выберите курс:",
        reply_markup=get_courses_kb()
    )
    await state.set_state(AddHomeworkStates.delete_test)

@router.callback_query(AddHomeworkStates.select_course, F.data.startswith("course_"))
async def select_subject(callback: CallbackQuery, state: FSMContext):
    """Выбор предмета для ДЗ"""
    logger.info("Вызван обработчик select_subject")
    course_id = callback.data
    course_name = "Интенсив. География" if course_id == "course_geo" else "Интенсив. Математика"
    
    await state.update_data(course_id=course_id, course_name=course_name)
    
    await callback.message.edit_text(
        f"Курс: {course_name}\n\n"
        "Выберите предмет для добавления домашнего задания:",
        reply_markup=get_subjects_kb(course_id)
    )
    await state.set_state(AddHomeworkStates.select_subject)

@router.callback_query(AddHomeworkStates.select_subject, F.data.startswith("sub_"))
async def select_lesson(callback: CallbackQuery, state: FSMContext):
    """Выбор урока для ДЗ"""
    logger.info("Вызван обработчик select_lesson")
    subject_id = callback.data
    
    # Словарь с названиями предметов
    subject_names = {
        "sub_kz": "История Казахстана",
        "sub_mathlit": "Математическая грамотность",
        "sub_math": "Математика",
        "sub_geo": "География",
        "sub_bio": "Биология",
        "sub_chem": "Химия",
        "sub_inf": "Информатика"
    }
    
    subject_name = subject_names.get(subject_id, "Неизвестный предмет")
    
    user_data = await state.get_data()
    course_name = user_data.get("course_name", "")
    
    await state.update_data(subject_id=subject_id, subject_name=subject_name)
    
    await callback.message.edit_text(
        f"Курс: {course_name}\n"
        f"Предмет: {subject_name}\n\n"
        "Выберите урок для добавления домашнего задания:",
        reply_markup=get_lessons_kb(subject_id)
    )
    await state.set_state(AddHomeworkStates.select_lesson)

register_test_handlers(router, AddHomeworkStates, "manager")

@router.callback_query(AddHomeworkStates.confirm_test, F.data == "confirm_test")
async def save_homework(callback: CallbackQuery, state: FSMContext):
    """Сохранение ДЗ в базу данных"""
    logger.info("Вызван обработчик save_homework")
    user_data = await state.get_data()
    
    # Здесь должен быть код для сохранения ДЗ в базу данных
    # ...
    
    await callback.message.edit_text(
        "✅ Домашнее задание успешно создано и сохранено!",
        reply_markup=get_courses_kb()  # Возвращаемся к выбору курса для добавления нового ДЗ
    )
    await state.set_state(AddHomeworkStates.select_course)

@router.callback_query(AddHomeworkStates.confirm_test, F.data == "edit_test")
async def edit_homework(callback: CallbackQuery, state: FSMContext):
    """Редактирование ДЗ"""
    logger.info("Вызван обработчик edit_homework")
    # Возвращаемся к началу процесса
    await callback.message.edit_text(
        "Выберите курс для добавления домашнего задания:",
        reply_markup=get_courses_kb()
    )
    await state.set_state(AddHomeworkStates.select_course)

@router.callback_query(AddHomeworkStates.confirm_test, F.data == "cancel_test")
async def cancel_homework(callback: CallbackQuery, state: FSMContext):
    """Отмена создания ДЗ"""
    logger.info("Вызван обработчик cancel_homework")
    await callback.message.edit_text(
        "❌ Создание домашнего задания отменено."
    )
    await show_manager_main_menu(callback, state)

# Обработчики для удаления ДЗ
@router.callback_query(AddHomeworkStates.main, F.data == "manager_delete_homework")
async def select_homework_to_delete(callback: CallbackQuery, state: FSMContext):
    """Выбор ДЗ для удаления"""
    logger.info("Вызван обработчик select_homework_to_delete")
    # Сначала выбираем курс, предмет и урок
    await callback.message.edit_text(
        "Выберите курс:",
        reply_markup=get_courses_kb()
    )
    await state.set_state(AddHomeworkStates.delete_test)

@router.callback_query(AddHomeworkStates.delete_test, F.data.startswith("course_"))
async def select_subject_for_delete(callback: CallbackQuery, state: FSMContext):
    """Выбор предмета для удаления ДЗ"""
    logger.info("Вызван обработчик select_subject_for_delete")
    course_id = callback.data
    await state.update_data(course_id=course_id)
    
    await callback.message.edit_text(
        "Выберите предмет:",
        reply_markup=get_subjects_kb(course_id)
    )

@router.callback_query(AddHomeworkStates.delete_test, F.data.startswith("sub_"))
async def select_lesson_for_delete(callback: CallbackQuery, state: FSMContext):
    """Выбор урока для удаления ДЗ"""
    logger.info("Вызван обработчик select_lesson_for_delete")
    subject_id = callback.data
    user_data = await state.get_data()
    course_id = user_data.get("course_id", "")

    await state.update_data(subject_id=subject_id)

    await callback.message.edit_text(
        "Выберите урок:",
        reply_markup=get_lessons_kb(subject_id)
    )

@router.callback_query(AddHomeworkStates.delete_test, F.data.startswith("lesson_"))
async def show_homeworks_to_delete(callback: CallbackQuery, state: FSMContext):
    """Показ списка ДЗ для удаления"""
    logger.info("Вызван обработчик show_homeworks_to_delete")
    lesson_id = callback.data
    await state.update_data(lesson_id=lesson_id)

    await callback.message.edit_text(
        "Выберите домашнее задание для удаления:",
        reply_markup=get_homeworks_list_kb(lesson_id)
    )
    await state.set_state(AddHomeworkStates.select_test_to_delete)

@router.callback_query(AddHomeworkStates.select_test_to_delete, F.data.startswith("delete_hw_"))
async def confirm_delete_homework(callback: CallbackQuery, state: FSMContext):
    """Подтверждение удаления ДЗ"""
    logger.info("Вызван обработчик confirm_delete_homework")
    homework_id = callback.data.replace("delete_hw_", "")
    await state.update_data(homework_id=homework_id)

    # В реальном приложении здесь будет запрос к базе данных
    homework_name = "Неизвестное ДЗ"
    if homework_id == "hw_1":
        homework_name = "Базовое ДЗ по алканам"
    elif homework_id == "hw_2":
        homework_name = "Углубленное ДЗ по алканам"
    elif homework_id == "hw_3":
        homework_name = "ДЗ на повторение"

    await callback.message.edit_text(
        f"Вы действительно хотите удалить домашнее задание '{homework_name}'?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Да, удалить", callback_data="confirm_delete")],
            [InlineKeyboardButton(text="❌ Нет, отмена", callback_data="cancel_delete")]
        ])
    )

@router.callback_query(F.data == "confirm_delete")
async def delete_homework(callback: CallbackQuery, state: FSMContext):
    """Удаление ДЗ"""
    logger.info("Вызван обработчик delete_homework")
    user_data = await state.get_data()
    homework_id = user_data.get("homework_id", "")

    # В реальном приложении здесь будет код для удаления ДЗ из базы данных
    # ...

    await callback.message.edit_text(
        "✅ Домашнее задание успешно удалено!",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
           *get_main_menu_back_button()
        ])
    )

@router.callback_query(F.data == "cancel_delete")
async def cancel_delete_homework(callback: CallbackQuery, state: FSMContext):
    """Отмена удаления ДЗ"""
    logger.info("Вызван обработчик cancel_delete_homework")
    user_data = await state.get_data()
    lesson_id = user_data.get("lesson_id", "")

    await callback.message.edit_text(
        "Выберите домашнее задание для удаления:",
        reply_markup=get_homeworks_list_kb(lesson_id)
    )
    await state.set_state(AddHomeworkStates.select_test_to_delete)



