import logging
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from .keyboards import (
    get_photo_skip_kb, get_correct_answer_kb,
    get_time_limit_kb, get_add_question_kb,
    get_confirm_test_kb
)
from common.keyboards import get_home_and_back_kb, get_home_kb

# Настройка логирования
logger = logging.getLogger(__name__)


async def enter_test_name(callback: CallbackQuery, state: FSMContext):
    """Ввод названия ДЗ"""
    logger.info("Вызван обработчик enter_test_name")
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
        "Введите название домашнего задания (например, 'Базовое', 'Углубленное', 'Повторение'):",
        reply_markup=get_home_kb()
    )


async def start_adding_questions(message: Message, state: FSMContext):
    """Начало добавления вопросов"""
    logger.info("Вызван обработчик start_adding_questions")
    test_name = message.text.strip()

    if not test_name:
        await message.answer("Название не может быть пустым. Пожалуйста, введите название домашнего задания:")
        return

    user_data = await state.get_data()
    course_name = user_data.get("course_name", "")
    subject_name = user_data.get("subject_name", "")
    lesson_name = user_data.get("lesson_name", "")

    await state.update_data(
        test_name=test_name,
        questions=[],
        current_question={}
    )

    await message.answer(
        f"Курс: {course_name}\n"
        f"Предмет: {subject_name}\n"
        f"Урок: {lesson_name}\n"
        f"Название ДЗ: {test_name}\n\n"
        "Теперь добавим вопросы. Введите текст первого вопроса:",
        reply_markup=get_home_and_back_kb()
    )


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


async def skip_photo(callback: CallbackQuery, state: FSMContext):
    """Пропуск добавления фото"""
    logger.info("Вызван обработчик skip_photo")
    await request_topic(callback.message, state)


async def process_question_photo(message: Message, state: FSMContext):
    """Обработка фото для вопроса"""
    logger.info("Вызван обработчик process_question_photo")
    photo = message.photo[-1]
    file_id = photo.file_id

    user_data = await state.get_data()
    current_question = user_data.get("current_question", {})
    current_question["photo_id"] = file_id

    await state.update_data(current_question=current_question)
    await request_topic(message, state)


async def request_topic(message: Message, state: FSMContext):
    """Запрос номера микротемы"""
    await message.answer(
        "Введите номер микротемы:"
    )


async def process_topic(message: Message, state: FSMContext, states_group):
    """Обработка выбора микротемы"""
    try:
        topic_number = int(message.text.strip())
        topic_id = f"topic_{topic_number}"

        # Словарь с названиями микротем
        topic_names = {
            "topic_1": "Строение алканов",
            "topic_2": "Номенклатура алканов",
            "topic_3": "Физические свойства алканов",
            "topic_4": "Химические свойства алканов"
        }

        topic_name = topic_names.get(topic_id, f"Микротема {topic_number}")

        user_data = await state.get_data()
        current_question = user_data.get("current_question", {})
        current_question["topic_id"] = topic_id
        current_question["topic_name"] = topic_name

        await state.update_data(current_question=current_question)
        await state.set_state(states_group.enter_answer_options)

        await message.answer(
            "Введите 5 вариантов ответа, каждый с новой строки в формате:\n"
            "A. Первый вариант\n"
            "B. Второй вариант\n"
            "C. Третий вариант\n"
            "D. Четвертый вариант\n"
            "E. Пятый вариант"
        )

    except ValueError:
        await message.answer("Пожалуйста, введите корректное число для номера микротемы.")


async def enter_answer_options(message: Message, state: FSMContext):
    """Ввод вариантов ответов"""
    logger.info("Вызван обработчик enter_answer_options")
    topic_id = 'topic_'+message.data

    # Словарь с названиями микротем
    topic_names = {
        "topic_1": "Строение алканов",
        "topic_2": "Номенклатура алканов",
        "topic_3": "Физические свойства алканов",
        "topic_4": "Химические свойства алканов"
    }

    topic_name = topic_names.get(topic_id, "Неизвестная микротема")

    user_data = await state.get_data()
    current_question = user_data.get("current_question", {})
    current_question["topic_id"] = topic_id
    current_question["topic_name"] = topic_name

    await state.update_data(current_question=current_question)

    await message.answer(
        "Введите 5 вариантов ответа, каждый с новой строки в формате:\n"
        "A. Первый вариант\n"
        "B. Второй вариант\n"
        "C. Третий вариант\n"
        "D. Четвертый вариант\n"
        "E. Пятый вариант"
    )


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


async def add_more_question(callback: CallbackQuery, state: FSMContext):
    """Добавление еще одного вопроса"""
    logger.info("Вызван обработчик add_more_question")
    await callback.message.edit_text("Введите текст следующего вопроса:")


async def set_time_limit(callback: CallbackQuery, state: FSMContext):
    """Установка времени на ответ"""
    logger.info("Вызван обработчик set_time_limit")
    await callback.message.edit_text(
        "Выберите время на ответ для одного вопроса:",
        reply_markup=get_time_limit_kb()
    )


async def confirm_test(callback: CallbackQuery, state: FSMContext):
    """Подтверждение создания ДЗ"""
    logger.info("Вызван обработчик confirm_test")
    time_limit = int(callback.data.replace("time_", ""))

    user_data = await state.get_data()
    course_name = user_data.get("course_name", "")
    subject_name = user_data.get("subject_name", "")
    lesson_name = user_data.get("lesson_name", "")
    test_name = user_data.get("test_name", "")
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
        f"Название ДЗ: {test_name}\n"
        f"Количество вопросов: {len(questions)}\n"
        f"Время на ответ: {time_text}\n\n"
        "Подтвердите создание домашнего задания:"
    )

    await callback.message.edit_text(
        confirmation_text,
        reply_markup=get_confirm_test_kb()
    )

