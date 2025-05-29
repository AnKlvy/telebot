from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
import logging
import os
from ..keyboards.homework import (
    get_courses_kb, get_subjects_kb, get_lessons_kb, get_topics_kb,
    get_time_limit_kb, get_correct_answer_kb, get_add_question_kb,
    get_confirm_homework_kb, get_homeworks_list_kb, get_photo_skip_kb, get_homework_management_kb
)
from .main import show_manager_main_menu

from aiogram.fsm.state import State, StatesGroup

class AddHomeworkStates(StatesGroup):
    select_course = State()
    select_subject = State()
    select_lesson = State()
    enter_homework_name = State()
    add_question = State()
    select_topic = State()
    enter_question_text = State()
    add_question_photo = State()
    enter_answer_options = State()
    select_correct_answer = State()
    set_time_limit = State()
    confirm_homework = State()
    delete_homework = State()
    select_homework_to_delete = State()

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

@router.callback_query(F.data == "manager_add_homework")
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
    await state.set_state(AddHomeworkStates.delete_homework)

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

@router.callback_query(AddHomeworkStates.select_lesson, F.data.startswith("lesson_"))
async def enter_homework_name(callback: CallbackQuery, state: FSMContext):
    """Ввод названия ДЗ"""
    logger.info("Вызван обработчик enter_homework_name")
    lesson_id = callback.data
    
    # Словарь с названиями уроков
    lesson_names = {
        "lesson_alkanes": "Алканы",
        "lesson_isomeria": "Изомерия",
        "lesson_acids": "Кислоты"
    }
    
    lesson_name = lesson_names.get(lesson_id, "Неизвестный урок")
    
    user_data = await state.get_data()
    course_name = user_data.get("course_name", "")
    subject_name = user_data.get("subject_name", "")
    
    await state.update_data(lesson_id=lesson_id, lesson_name=lesson_name)
    
    await callback.message.edit_text(
        f"Курс: {course_name}\n"
        f"Предмет: {subject_name}\n"
        f"Урок: {lesson_name}\n\n"
        "Введите название домашнего задания (например, 'Базовое', 'Углубленное', 'Повторение'):"
    )
    await state.set_state(AddHomeworkStates.enter_homework_name)

@router.message(AddHomeworkStates.enter_homework_name)
async def start_adding_questions(message: Message, state: FSMContext):
    """Начало добавления вопросов"""
    logger.info("Вызван обработчик start_adding_questions")
    homework_name = message.text.strip()
    
    if not homework_name:
        await message.answer("Название не может быть пустым. Пожалуйста, введите название домашнего задания:")
        return
    
    user_data = await state.get_data()
    course_name = user_data.get("course_name", "")
    subject_name = user_data.get("subject_name", "")
    lesson_name = user_data.get("lesson_name", "")
    
    await state.update_data(
        homework_name=homework_name,
        questions=[],
        current_question={}
    )
    
    await message.answer(
        f"Курс: {course_name}\n"
        f"Предмет: {subject_name}\n"
        f"Урок: {lesson_name}\n"
        f"Название ДЗ: {homework_name}\n\n"
        "Теперь добавим вопросы. Введите текст первого вопроса:"
    )
    await state.set_state(AddHomeworkStates.enter_question_text)

@router.message(AddHomeworkStates.enter_question_text)
async def add_question_photo(message: Message, state: FSMContext):
    """Добавление фото к вопросу"""
    logger.info("Вызван обработчик add_question_photo")
    question_text = message.text.strip()
    
    if not question_text:
        await message.answer("Текст вопроса не может быть пустым. Пожалуйста, введите текст вопроса:")
        return
    
    await state.update_data(current_question={"text": question_text})
    
    await message.answer(
        "Отправьте фото для этого вопроса (если нужно) или нажмите 'Пропустить':",
        reply_markup=get_photo_skip_kb()
    )
    await state.set_state(AddHomeworkStates.add_question_photo)

@router.message(AddHomeworkStates.add_question_photo, F.photo)
async def process_question_photo(message: Message, state: FSMContext):
    """Обработка фото для вопроса"""
    logger.info("Вызван обработчик process_question_photo")
    photo = message.photo[-1]
    file_id = photo.file_id
    
    user_data = await state.get_data()
    current_question = user_data.get("current_question", {})
    current_question["photo_id"] = file_id
    
    await state.update_data(current_question=current_question)
    
    await select_topic(message, state)

@router.callback_query(AddHomeworkStates.add_question_photo, F.data == "skip_photo")
async def skip_photo(callback: CallbackQuery, state: FSMContext):
    """Пропуск добавления фото"""
    logger.info("Вызван обработчик skip_photo")
    await select_topic(callback.message, state)

async def select_topic(message: Message, state: FSMContext):
    """Выбор микротемы для вопроса"""
    logger.info("Вызвана функция select_topic")
    user_data = await state.get_data()
    lesson_id = user_data.get("lesson_id", "")
    
    await message.answer(
        "Выберите микротему, к которой относится этот вопрос:",
        reply_markup=get_topics_kb(lesson_id)
    )
    await state.set_state(AddHomeworkStates.select_topic)

@router.callback_query(AddHomeworkStates.select_topic, F.data.startswith("topic_"))
async def enter_answer_options(callback: CallbackQuery, state: FSMContext):
    """Ввод вариантов ответов"""
    logger.info("Вызван обработчик enter_answer_options")
    topic_id = callback.data
    
    # Словарь с названиями микротем
    topic_names = {
        "topic_topic_1": "Строение алканов",
        "topic_topic_2": "Номенклатура алканов",
        "topic_topic_3": "Физические свойства алканов",
        "topic_topic_4": "Химические свойства алканов"
    }
    
    topic_name = topic_names.get(topic_id, "Неизвестная микротема")
    
    user_data = await state.get_data()
    current_question = user_data.get("current_question", {})
    current_question["topic_id"] = topic_id
    current_question["topic_name"] = topic_name
    
    await state.update_data(current_question=current_question)
    
    await callback.message.edit_text(
        "Введите 5 вариантов ответа, каждый с новой строки в формате:\n"
        "A. Первый вариант\n"
        "B. Второй вариант\n"
        "C. Третий вариант\n"
        "D. Четвертый вариант\n"
        "E. Пятый вариант"
    )
    await state.set_state(AddHomeworkStates.enter_answer_options)

@router.message(AddHomeworkStates.enter_answer_options)
async def select_correct_answer(message: Message, state: FSMContext):
    """Выбор правильного ответа"""
    logger.info("Вызван обработчик select_correct_answer")
    answer_text = message.text.strip()
    
    # Проверяем, что введены все 5 вариантов
    lines = answer_text.split("\n")
    if len(lines) < 5:
        await message.answer(
            "Необходимо ввести 5 вариантов ответа, каждый с новой строки. Пожалуйста, попробуйте снова:"
        )
        return
    
    # Проверяем формат вариантов и заменяем кириллические буквы на латинские
    options = {}
    cyrillic_to_latin = {
        'А': 'A', 'В': 'B', 'С': 'C', 'Е': 'E', 'а': 'a', 'в': 'b', 'с': 'c', 'е': 'e'
    }
    
    for line in lines[:5]:  # Берем только первые 5 строк
        if not line or "." not in line:
            continue
        
        parts = line.split(".", 1)
        if len(parts) != 2:
            continue
        
        letter = parts[0].strip().upper()
        # Заменяем кириллические буквы на латинские
        if letter in cyrillic_to_latin:
            letter = cyrillic_to_latin[letter]
        
        text = parts[1].strip()
        
        if letter in ["A", "B", "C", "D", "E"]:
            options[letter] = text
    
    # Проверяем, что все варианты введены
    if len(options) < 5 or not all(letter in options for letter in ["A", "B", "C", "D", "E"]):
        await message.answer(
            "Необходимо ввести все 5 вариантов ответа (A, B, C, D, E). Пожалуйста, попробуйте снова:"
        )
        return
    
    user_data = await state.get_data()
    current_question = user_data.get("current_question", {})
    current_question["options"] = options
    
    await state.update_data(current_question=current_question)
    
    await message.answer(
        "Выберите правильный вариант ответа:",
        reply_markup=get_correct_answer_kb()
    )
    await state.set_state(AddHomeworkStates.select_correct_answer)

@router.callback_query(AddHomeworkStates.select_correct_answer, F.data.startswith("correct_"))
async def save_question(callback: CallbackQuery, state: FSMContext):
    """Сохранение вопроса и переход к следующему"""
    logger.info("Вызван обработчик save_question")
    correct_answer = callback.data.replace("correct_", "")
    
    user_data = await state.get_data()
    current_question = user_data.get("current_question", {})
    current_question["correct_answer"] = correct_answer
    
    questions = user_data.get("questions", [])
    questions.append(current_question)
    
    await state.update_data(questions=questions, current_question={})
    
    await callback.message.edit_text(
        f"Вопрос добавлен! Всего вопросов: {len(questions)}",
        reply_markup=get_add_question_kb(len(questions))
    )
    await state.set_state(AddHomeworkStates.add_question)

@router.callback_query(AddHomeworkStates.add_question, F.data == "add_more_question")
async def add_more_question(callback: CallbackQuery, state: FSMContext):
    """Добавление еще одного вопроса"""
    logger.info("Вызван обработчик add_more_question")
    await callback.message.edit_text("Введите текст следующего вопроса:")
    await state.set_state(AddHomeworkStates.enter_question_text)

@router.callback_query(AddHomeworkStates.add_question, F.data == "finish_adding_questions")
async def set_time_limit(callback: CallbackQuery, state: FSMContext):
    """Установка времени на ответ"""
    logger.info("Вызван обработчик set_time_limit")
    await callback.message.edit_text(
        "Выберите время на ответ для одного вопроса:",
        reply_markup=get_time_limit_kb()
    )
    await state.set_state(AddHomeworkStates.set_time_limit)

@router.callback_query(AddHomeworkStates.set_time_limit, F.data.startswith("time_"))
async def confirm_homework(callback: CallbackQuery, state: FSMContext):
    """Подтверждение создания ДЗ"""
    logger.info("Вызван обработчик confirm_homework")
    time_limit = int(callback.data.replace("time_", ""))
    
    user_data = await state.get_data()
    course_name = user_data.get("course_name", "")
    subject_name = user_data.get("subject_name", "")
    lesson_name = user_data.get("lesson_name", "")
    homework_name = user_data.get("homework_name", "")
    questions = user_data.get("questions", [])
    
    # Форматируем время
    time_text = f"{time_limit} сек."
    if time_limit >= 60:
        minutes = time_limit // 60
        seconds = time_limit % 60
        time_text = f"{minutes} мин."
        if seconds > 0:
            time_text += f" {seconds} сек."
    
    await state.update_data(time_limit=time_limit)
    
    # Формируем текст для подтверждения
    confirmation_text = (
        f"Курс: {course_name}\n"
        f"Предмет: {subject_name}\n"
        f"Урок: {lesson_name}\n"
        f"Название ДЗ: {homework_name}\n"
        f"Количество вопросов: {len(questions)}\n"
        f"Время на ответ: {time_text}\n\n"
        "Подтвердите создание домашнего задания:"
    )
    
    await callback.message.edit_text(
        confirmation_text,
        reply_markup=get_confirm_homework_kb()
    )
    await state.set_state(AddHomeworkStates.confirm_homework)

@router.callback_query(AddHomeworkStates.confirm_homework, F.data == "confirm_homework")
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

@router.callback_query(AddHomeworkStates.confirm_homework, F.data == "edit_homework")
async def edit_homework(callback: CallbackQuery, state: FSMContext):
    """Редактирование ДЗ"""
    logger.info("Вызван обработчик edit_homework")
    # Возвращаемся к началу процесса
    await callback.message.edit_text(
        "Выберите курс для добавления домашнего задания:",
        reply_markup=get_courses_kb()
    )
    await state.set_state(AddHomeworkStates.select_course)

@router.callback_query(AddHomeworkStates.confirm_homework, F.data == "cancel_homework")
async def cancel_homework(callback: CallbackQuery, state: FSMContext):
    """Отмена создания ДЗ"""
    logger.info("Вызван обработчик cancel_homework")
    await callback.message.edit_text(
        "❌ Создание домашнего задания отменено."
    )
    await show_manager_main_menu(callback, state)

# Обработчики для удаления ДЗ
@router.callback_query(F.data == "manager_delete_homework")
async def select_homework_to_delete(callback: CallbackQuery, state: FSMContext):
    """Выбор ДЗ для удаления"""
    logger.info("Вызван обработчик select_homework_to_delete")
    # Сначала выбираем курс, предмет и урок
    await callback.message.edit_text(
        "Выберите курс:",
        reply_markup=get_courses_kb()
    )
    await state.set_state(AddHomeworkStates.delete_homework)

@router.callback_query(AddHomeworkStates.delete_homework, F.data.startswith("course_"))
async def select_subject_for_delete(callback: CallbackQuery, state: FSMContext):
    """Выбор предмета для удаления ДЗ"""
    logger.info("Вызван обработчик select_subject_for_delete")
    course_id = callback.data
    await state.update_data(course_id=course_id)
    
    await callback.message.edit_text(
        "Выберите предмет:",
        reply_markup=get_subjects_kb(course_id)
    )

@router.callback_query(AddHomeworkStates.delete_homework, F.data.startswith("sub_"))
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

@router.callback_query(AddHomeworkStates.delete_homework, F.data.startswith("lesson_"))
async def show_homeworks_to_delete(callback: CallbackQuery, state: FSMContext):
    """Показ списка ДЗ для удаления"""
    logger.info("Вызван обработчик show_homeworks_to_delete")
    lesson_id = callback.data
    await state.update_data(lesson_id=lesson_id)

    await callback.message.edit_text(
        "Выберите домашнее задание для удаления:",
        reply_markup=get_homeworks_list_kb(lesson_id)
    )
    await state.set_state(AddHomeworkStates.select_homework_to_delete)

@router.callback_query(AddHomeworkStates.select_homework_to_delete, F.data.startswith("delete_hw_"))
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
            [InlineKeyboardButton(text="⬅️ Назад к списку ДЗ", callback_data="back_to_homeworks")],
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main")]
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
    await state.set_state(AddHomeworkStates.select_homework_to_delete)

@router.callback_query(F.data == "back_to_homeworks")
async def back_to_homeworks(callback: CallbackQuery, state: FSMContext):
    """Возврат к списку ДЗ"""
    logger.info("Вызван обработчик back_to_homeworks")
    user_data = await state.get_data()
    lesson_id = user_data.get("lesson_id", "")

    await callback.message.edit_text(
        "Выберите домашнее задание для удаления:",
        reply_markup=get_homeworks_list_kb(lesson_id)
    )
    await state.set_state(AddHomeworkStates.select_homework_to_delete)

# Обработчики для навигации назад
@router.callback_query(F.data == "back_to_question_text")
async def back_to_question_text(callback: CallbackQuery, state: FSMContext):
    """Возврат к вводу текста вопроса"""
    logger.info("Вызван обработчик back_to_question_text")
    await callback.message.edit_text("Введите текст вопроса:")
    await state.set_state(AddHomeworkStates.enter_question_text)

@router.callback_query(F.data == "back_to_answer_options")
async def back_to_answer_options(callback: CallbackQuery, state: FSMContext):
    """Возврат к вводу вариантов ответа"""
    logger.info("Вызван обработчик back_to_answer_options")
    await callback.message.edit_text(
        "Введите 5 вариантов ответа, каждый с новой строки в формате:\n"
        "A. Первый вариант\n"
        "B. Второй вариант\n"
        "C. Третий вариант\n"
        "D. Четвертый вариант\n"
        "E. Пятый вариант"
    )
    await state.set_state(AddHomeworkStates.enter_answer_options)

@router.callback_query(F.data == "back_to_questions")
async def back_to_questions(callback: CallbackQuery, state: FSMContext):
    """Возврат к добавлению вопросов"""
    logger.info("Вызван обработчик back_to_questions")
    user_data = await state.get_data()
    questions = user_data.get("questions", [])

    await callback.message.edit_text(
        f"Всего вопросов: {len(questions)}",
        reply_markup=get_add_question_kb(len(questions))
    )
    await state.set_state(AddHomeworkStates.add_question)

@router.callback_query(F.data == "back_to_homework_name")
async def back_to_homework_name(callback: CallbackQuery, state: FSMContext):
    """Возврат к вводу названия ДЗ"""
    logger.info("Вызван обработчик back_to_homework_name")
    user_data = await state.get_data()
    course_name = user_data.get("course_name", "")
    subject_name = user_data.get("subject_name", "")
    lesson_name = user_data.get("lesson_name", "")

    await callback.message.edit_text(
        f"Курс: {course_name}\n"
        f"Предмет: {subject_name}\n"
        f"Урок: {lesson_name}\n\n"
        "Введите название домашнего задания (например, 'Базовое', 'Углубленное', 'Повторение'):"
    )
    await state.set_state(AddHomeworkStates.enter_homework_name)