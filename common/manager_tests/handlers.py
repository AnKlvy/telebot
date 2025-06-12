import logging
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from .keyboards import (
    get_photo_skip_kb, get_correct_answer_kb,
    get_time_limit_kb, get_add_question_kb,
    get_confirm_test_kb
)
from manager.keyboards.homework import get_photo_edit_kb
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
        await message.answer("Название не может быть пустым. Пожалуйста, введите название теста:")
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

    # Проверяем, это бонусный тест или обычное ДЗ
    current_state = await state.get_state()
    if "BonusTest" in current_state:
        info_text = f"🧪 Бонусный тест: {test_name}\n\n"
    else:
        info_text = (
            f"Курс: {course_name}\n"
            f"Предмет: {subject_name}\n"
            f"Урок: {lesson_name}\n"
            f"🏷 Название ДЗ: {test_name}\n\n"
        )

    # Показываем название с возможностью редактирования
    from manager.keyboards.homework import get_step_edit_kb
    await message.answer(
        info_text + "Название сохранено! Хотите изменить или продолжить?",
        reply_markup=get_step_edit_kb("test_name", True)
    )


async def add_question_photo(message: Message, state: FSMContext):
    """Добавление фото к вопросу"""
    logger.info("Вызван обработчик add_question_photo")
    question_text = message.text.strip()

    if not question_text:
        await message.answer("Текст вопроса не может быть пустым. Пожалуйста, введите текст вопроса:")
        return

    await state.update_data(current_question={"text": question_text})

    # Показываем текст вопроса с возможностью редактирования
    from manager.keyboards.homework import get_step_edit_kb
    await message.answer(
        f"📝 Текст вопроса:\n{question_text}\n\nХотите изменить текст или продолжить?",
        reply_markup=get_step_edit_kb("question_text", True)
    )


async def skip_photo(callback: CallbackQuery, state: FSMContext):
    """Пропуск добавления фото"""
    logger.info("Вызван обработчик skip_photo")

    # Показываем что фото пропущено с возможностью добавить
    from manager.keyboards.homework import get_step_edit_kb
    await callback.message.edit_text(
        "📷 Фото пропущено (вопрос без изображения)\n\nХотите добавить фото или продолжить?",
        reply_markup=get_step_edit_kb("photo", False)
    )


async def process_question_photo(message: Message, state: FSMContext):
    """Обработка фото для вопроса"""
    logger.info("Вызван обработчик process_question_photo")
    photo = message.photo[-1]
    file_id = photo.file_id

    user_data = await state.get_data()
    current_question = user_data.get("current_question", {})
    current_question["photo_id"] = file_id

    await state.update_data(current_question=current_question)

    # Показываем фото с возможностью редактирования
    from manager.keyboards.homework import get_step_edit_kb
    await message.answer_photo(
        photo=file_id,
        caption="📷 Фото добавлено! Хотите изменить фото или продолжить?",
        reply_markup=get_step_edit_kb("photo", True)
    )


async def request_topic(message: Message, state: FSMContext):
    """Запрос номера микротемы"""
    await message.answer(
        "Введите номер микротемы:"
    )


async def process_topic(message: Message, state: FSMContext, states_group):
    """Обработка выбора микротемы"""
    try:
        topic_number = int(message.text.strip())

        # Проверяем диапазон номера микротемы (убираем ограничение в 50)
        if topic_number < 1:
            await message.answer("❌ Номер микротемы должен быть больше 0. Попробуйте еще раз:")
            return

        # Получаем данные о предмете для проверки микротемы
        user_data = await state.get_data()
        subject_id = user_data.get("subject_id")

        if not subject_id:
            await message.answer("❌ Ошибка: предмет не выбран. Начните создание ДЗ заново.")
            return

        # Импортируем репозитории для проверки микротемы
        from database import MicrotopicRepository, SubjectRepository

        # Получаем предмет и его микротемы
        subject = await SubjectRepository.get_by_id(subject_id)
        if not subject:
            await message.answer("❌ Ошибка: предмет не найден. Начните создание ДЗ заново.")
            return

        microtopics = await MicrotopicRepository.get_by_subject(subject_id)

        # Ищем микротему по номеру в поле number
        microtopic = await MicrotopicRepository.get_by_number(subject_id, topic_number)

        if microtopic:
            microtopic_id = microtopic.id
            microtopic_name = microtopic.name
        else:
            microtopic_id = None
            microtopic_name = None

        # Если микротема не найдена, требуем ввести заново
        if not microtopic_id:
            from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

            # Показываем доступные микротемы для справки
            available_topics = ""
            if microtopics:
                available_topics = "\n📋 Доступные микротемы:\n"
                for mt in microtopics[:10]:  # Показываем первые 10
                    available_topics += f"   {mt.number}. {mt.name}\n"

                if len(microtopics) > 10:
                    available_topics += f"   ... и еще {len(microtopics) - 10} микротем\n"

            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="➕ Добавить новую микротему", callback_data=f"add_microtopic_{subject_id}_{topic_number}")],
                [InlineKeyboardButton(text="🔄 Ввести номер заново", callback_data="retry_microtopic")]
            ])

            await message.answer(
                f"❌ Микротема с номером {topic_number} не найдена в базе данных для предмета '{subject.name}'.\n"
                f"{available_topics}\n"
                "Выберите действие:",
                reply_markup=keyboard
            )
            return
        else:
            await message.answer(
                f"✅ Выбрана микротема: {microtopic_name}\n\n"
                "Введите варианты ответа (от 2 до 10), каждый с новой строки.\n\n"
                "Поддерживаемые форматы:\n"
                "• A. Первый вариант\n"
                "• B Второй вариант\n"
                "• Третий вариант\n"
                "• Четвертый вариант\n\n"
                "Минимум 2 варианта, максимум 10 вариантов."
            )

            # Сохраняем данные микротемы
            current_question = user_data.get("current_question", {})
            current_question["microtopic_id"] = microtopic_id
            current_question["microtopic_name"] = microtopic_name
            current_question["topic_number"] = topic_number

            await state.update_data(current_question=current_question)
            await state.set_state(states_group.enter_answer_options)

    except ValueError:
        await message.answer("❌ Пожалуйста, введите корректное число для номера микротемы:")
    except Exception as e:
        logger.error(f"Ошибка при обработке микротемы: {e}")
        await message.answer("❌ Произошла ошибка при обработке микротемы. Попробуйте еще раз:")


async def handle_microtopic_retry(callback: CallbackQuery, state: FSMContext):
    """Обработка повторного ввода номера микротемы"""
    await callback.message.edit_text(
        "Введите номер микротемы:"
    )
    await callback.answer()


async def handle_add_microtopic(callback: CallbackQuery, state: FSMContext):
    """Обработка добавления новой микротемы"""
    # Извлекаем subject_id и topic_number из callback_data
    data_parts = callback.data.split("_")  # add_microtopic_{subject_id}_{topic_number}
    if len(data_parts) >= 4:
        subject_id = int(data_parts[2])
        topic_number = int(data_parts[3])

        # Сохраняем данные для создания микротемы
        user_data = await state.get_data()
        await state.update_data(
            pending_microtopic_subject_id=subject_id,
            pending_microtopic_number=topic_number
        )

        await callback.message.edit_text(
            f"Введите название для микротемы №{topic_number}:"
        )

        # Устанавливаем состояние для ввода названия микротемы
        from manager.handlers.homework import AddHomeworkStates
        await state.set_state(AddHomeworkStates.add_microtopic_name)

    await callback.answer()


async def process_new_microtopic_name(message: Message, state: FSMContext):
    """Обработка названия новой микротемы"""
    try:
        microtopic_name = message.text.strip()

        if not microtopic_name:
            await message.answer("❌ Название микротемы не может быть пустым. Попробуйте еще раз:")
            return

        user_data = await state.get_data()
        subject_id = user_data.get("pending_microtopic_subject_id")
        topic_number = user_data.get("pending_microtopic_number")

        if not subject_id or not topic_number:
            await message.answer("❌ Ошибка: данные микротемы не найдены. Начните создание вопроса заново.")
            return

        # Импортируем репозиторий
        from database import MicrotopicRepository

        # Создаем новую микротему (номер присваивается автоматически)
        new_microtopic = await MicrotopicRepository.create(
            name=microtopic_name,
            subject_id=subject_id
        )

        await message.answer(
            f"✅ Микротема создана: {new_microtopic.number}. {new_microtopic.name}\n\n"
            "Теперь введите номер микротемы снова:"
        )

        # Очищаем временные данные
        await state.update_data(
            pending_microtopic_subject_id=None,
            pending_microtopic_number=None
        )

        # Возвращаемся к состоянию выбора микротемы
        from manager.handlers.homework import AddHomeworkStates
        await state.set_state(AddHomeworkStates.request_topic)

    except Exception as e:
        logger.error(f"Ошибка при создании микротемы: {e}")
        await message.answer("❌ Произошла ошибка при создании микротемы. Попробуйте еще раз:")





async def select_correct_answer(message: Message, state: FSMContext, states_group):
    """Выбор правильного ответа"""
    logger.info("Вызван обработчик select_correct_answer")
    answer_text = message.text.strip()

    # Проверяем, что введено минимум 2 варианта
    lines = answer_text.split("\n")
    if len(lines) < 2:
        await message.answer(
            "Необходимо ввести минимум 2 варианта ответа, каждый с новой строки. Пожалуйста, попробуйте снова:"
        )
        # Остаемся в том же состоянии для повторного ввода
        return

    # Проверяем формат вариантов и заменяем кириллические буквы на латинские
    options = {}
    cyrillic_to_latin = {
        'А': 'A', 'В': 'B', 'С': 'C', 'Д': 'D', 'Е': 'E', 'Ф': 'F', 'Г': 'G', 'Х': 'H', 'И': 'I', 'Й': 'J',
        'а': 'a', 'в': 'b', 'с': 'c', 'д': 'd', 'е': 'e', 'ф': 'f', 'г': 'g', 'х': 'h', 'и': 'i', 'й': 'j'
    }

    # Допустимые буквы для вариантов (до 10 вариантов)
    valid_letters = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]

    for line in lines[:10]:  # Берем максимум 10 строк
        line = line.strip()
        if not line:
            continue

        # Проверяем формат с точкой (A. Текст)
        if "." in line:
            parts = line.split(".", 1)
            if len(parts) == 2:
                letter = parts[0].strip().upper()
                text = parts[1].strip()
            else:
                continue
        # Проверяем формат без точки (A Текст или просто текст)
        else:
            # Если строка начинается с буквы и пробела
            if len(line) > 2 and line[1] == ' ':
                letter = line[0].upper()
                text = line[2:].strip()
            # Если это просто текст без буквы - автоматически присваиваем букву
            else:
                # Определяем следующую доступную букву
                used_letters = set(options.keys())
                letter = None
                for available_letter in valid_letters:
                    if available_letter not in used_letters:
                        letter = available_letter
                        break

                if letter is None:
                    continue  # Все буквы уже использованы

                text = line

        # Заменяем кириллические буквы на латинские
        if letter in cyrillic_to_latin:
            letter = cyrillic_to_latin[letter]

        if letter in valid_letters and text:
            options[letter] = text

    # Проверяем, что введено минимум 2 варианта
    if len(options) < 2:
        await message.answer(
            "❌ Необходимо ввести минимум 2 варианта ответа.\n\n"
            "Поддерживаемые форматы:\n"
            "• A. Первый вариант\n"
            "• B Второй вариант\n"
            "• Третий вариант\n\n"
            "Попробуйте снова:"
        )
        # Остаемся в том же состоянии для повторного ввода
        return

    # Проверяем, что варианты идут по порядку (A, B, C, ...)
    sorted_letters = sorted(options.keys())
    expected_letters = valid_letters[:len(options)]
    if sorted_letters != expected_letters:
        await message.answer(
            f"Варианты должны идти по порядку: {', '.join(expected_letters[:len(options)])}. Пожалуйста, попробуйте снова:"
        )
        return

    user_data = await state.get_data()
    current_question = user_data.get("current_question", {})
    current_question["options"] = options

    await state.update_data(current_question=current_question)

    # Показываем варианты ответов с возможностью редактирования
    options_text = ""
    for letter, text in sorted(options.items()):
        options_text += f"{letter}. {text}\n"

    from manager.keyboards.homework import get_step_edit_kb
    await message.answer(
        f"📝 Варианты ответов:\n{options_text}\nХотите изменить варианты или продолжить к выбору правильного ответа?",
        reply_markup=get_step_edit_kb("answer_options", True)
    )


async def save_question(callback: CallbackQuery, state: FSMContext):
    """Выбор правильного ответа и переход к выбору времени"""
    logger.info("Вызван обработчик save_question")
    correct_answer = callback.data.replace("correct_", "")

    user_data = await state.get_data()
    current_question = user_data.get("current_question", {})
    current_question["correct_answer"] = correct_answer

    await state.update_data(current_question=current_question)

    await callback.message.edit_text(
        "Выберите время на ответ для этого вопроса:",
        reply_markup=get_time_limit_kb()
    )


async def save_question_with_time(callback: CallbackQuery, state: FSMContext):
    """Сохранение вопроса с временем и переход к следующему"""
    logger.info("Вызван обработчик save_question_with_time")
    time_limit = int(callback.data.replace("time_", ""))

    user_data = await state.get_data()
    current_question = user_data.get("current_question", {})
    current_question["time_limit"] = time_limit

    questions = user_data.get("questions", [])
    questions.append(current_question)

    await state.update_data(questions=questions, current_question={})

    # Форматируем время для отображения
    time_text = f"{time_limit} сек."
    if time_limit >= 60:
        minutes = time_limit // 60
        seconds = time_limit % 60
        time_text = f"{minutes} мин."
        if seconds > 0:
            time_text += f" {seconds} сек."

    await callback.message.edit_text(
        f"Вопрос добавлен! Всего вопросов: {len(questions)}\n"
        f"Время на ответ: {time_text}",
        reply_markup=get_add_question_kb(len(questions))
    )


async def add_more_question(callback: CallbackQuery, state: FSMContext):
    """Добавление еще одного вопроса"""
    logger.info("Вызван обработчик add_more_question")
    await callback.message.edit_text("Введите текст следующего вопроса:")


async def finish_adding_questions(callback: CallbackQuery, state: FSMContext):
    """Завершение добавления вопросов и переход к подтверждению"""
    logger.info("Вызван обработчик finish_adding_questions")
    await confirm_test(callback, state)


async def confirm_test(callback: CallbackQuery, state: FSMContext):
    """Подтверждение создания ДЗ"""
    logger.info("Вызван обработчик confirm_test")

    user_data = await state.get_data()
    course_name = user_data.get("course_name", "")
    subject_name = user_data.get("subject_name", "")
    lesson_name = user_data.get("lesson_name", "")
    test_name = user_data.get("test_name", "")
    questions = user_data.get("questions", [])

    # Формируем информацию о времени для каждого вопроса
    questions_info = ""
    for i, question in enumerate(questions, 1):
        time_limit = question.get("time_limit", 30)  # По умолчанию 30 сек
        time_text = f"{time_limit} сек."
        if time_limit >= 60:
            minutes = time_limit // 60
            seconds = time_limit % 60
            time_text = f"{minutes} мин."
            if seconds > 0:
                time_text += f" {seconds} сек."

        questions_info += f"Вопрос {i}: {time_text}\n"

    # Формируем текст для подтверждения
    confirmation_text = (
        f"📋 ПРЕДВАРИТЕЛЬНЫЙ ПРОСМОТР ДЗ\n\n"
        f"📚 Курс: {course_name}\n"
        f"📖 Предмет: {subject_name}\n"
        f"📝 Урок: {lesson_name}\n"
        f"🏷 Название ДЗ: {test_name}\n"
        f"❓ Количество вопросов: {len(questions)}\n\n"
        f"⏱ Время на ответ:\n{questions_info}\n"
        "Подтвердите создание домашнего задания:"
    )

    await callback.message.edit_text(
        confirmation_text,
        reply_markup=get_confirm_test_kb()
    )


async def show_test_summary_with_edit(callback: CallbackQuery, state: FSMContext):
    """Показать сводку теста с возможностью редактирования"""
    user_data = await state.get_data()
    course_name = user_data.get("course_name", "")
    subject_name = user_data.get("subject_name", "")
    lesson_name = user_data.get("lesson_name", "")
    test_name = user_data.get("test_name", "")
    questions = user_data.get("questions", [])

    summary_text = (
        f"📋 ТЕКУЩЕЕ СОСТОЯНИЕ ДЗ\n\n"
        f"📚 Курс: {course_name} ✏️\n"
        f"📖 Предмет: {subject_name} ✏️\n"
        f"📝 Урок: {lesson_name} ✏️\n"
        f"🏷 Название ДЗ: {test_name} ✏️\n"
        f"❓ Вопросов добавлено: {len(questions)}\n\n"
        "Что хотите изменить?"
    )

    from manager.keyboards.homework import get_step_edit_kb
    await callback.message.edit_text(
        summary_text,
        reply_markup=get_step_edit_kb("summary", True)
    )


# ==================== ОБРАБОТЧИКИ РЕДАКТИРОВАНИЯ ====================

async def edit_test_name(callback: CallbackQuery, state: FSMContext, states_group):
    """Редактирование названия теста"""
    logger.info("Вызван обработчик edit_test_name")

    user_data = await state.get_data()
    current_name = user_data.get("test_name", "")

    await callback.message.edit_text(
        f"📝 Текущее название ДЗ: **{current_name}**\n\n"
        "Введите новое название домашнего задания:"
    )
    await state.set_state(states_group.edit_test_name)


async def process_edit_test_name(message: Message, state: FSMContext, states_group):
    """Обработка нового названия теста"""
    new_name = message.text.strip()

    if not new_name:
        await message.answer("❌ Название не может быть пустым. Попробуйте снова:")
        return

    await state.update_data(test_name=new_name)
    await message.answer(
        f"✅ Название ДЗ изменено на: {new_name}"
    )

    # Возвращаемся к сводке
    await show_test_summary_with_edit(message, state)


async def edit_question_text(callback: CallbackQuery, state: FSMContext, states_group, question_num: int):
    """Редактирование текста вопроса"""
    logger.info(f"Редактирование вопроса {question_num}")

    user_data = await state.get_data()
    questions = user_data.get("questions", [])

    if question_num <= len(questions):
        current_question = questions[question_num - 1]
        current_text = current_question.get("text", "")

        await callback.message.edit_text(
            f"📝 Текущий текст вопроса {question_num}:\n\n"
            f"**{current_text}**\n\n"
            "Введите новый текст вопроса:"
        )

        await state.update_data(editing_question_num=question_num)
        await state.set_state(states_group.edit_question_text)
    else:
        await callback.answer("❌ Вопрос не найден")


async def process_edit_question_text(message: Message, state: FSMContext):
    """Обработка нового текста вопроса"""
    new_text = message.text.strip()

    if not new_text:
        await message.answer("❌ Текст вопроса не может быть пустым. Попробуйте снова:")
        return

    user_data = await state.get_data()
    questions = user_data.get("questions", [])
    question_num = user_data.get("editing_question_num", 1)

    if question_num <= len(questions):
        questions[question_num - 1]["text"] = new_text
        await state.update_data(questions=questions)

        await message.answer(
            f"✅ Текст вопроса {question_num} изменен!"
        )

        # Показываем обновленную сводку
        await show_test_summary_with_edit(message, state)


async def edit_answer_options(callback: CallbackQuery, state: FSMContext, states_group, question_num: int):
    """Редактирование вариантов ответов"""
    logger.info(f"Редактирование вариантов ответов для вопроса {question_num}")

    user_data = await state.get_data()
    questions = user_data.get("questions", [])

    if question_num <= len(questions):
        current_question = questions[question_num - 1]
        current_options = current_question.get("options", {})

        options_text = ""
        for letter, text in sorted(current_options.items()):
            options_text += f"{letter}. {text}\n"

        await callback.message.edit_text(
            f"📝 Текущие варианты ответов для вопроса {question_num}:\n\n"
            f"{options_text}\n"
            "Введите новые варианты ответа (от 2 до 10), каждый с новой строки.\n\n"
            "Поддерживаемые форматы:\n"
            "• A. Первый вариант\n"
            "• B Второй вариант\n"
            "• Третий вариант\n"
            "• Четвертый вариант"
        )

        await state.update_data(editing_question_num=question_num)
        await state.set_state(states_group.edit_answer_options)
    else:
        await callback.answer("❌ Вопрос не найден")


async def process_edit_answer_options(message: Message, state: FSMContext, states_group):
    """Обработка новых вариантов ответов"""
    # Используем ту же логику, что и в основном обработчике
    answer_text = message.text.strip()
    lines = answer_text.split("\n")

    if len(lines) < 2:
        await message.answer(
            "❌ Необходимо ввести минимум 2 варианта ответа.\n\n"
            "Поддерживаемые форматы:\n"
            "• A. Первый вариант\n"
            "• B Второй вариант\n"
            "• Третий вариант\n\n"
            "Попробуйте снова:"
        )
        return

    # Парсим варианты ответов (используем ту же логику)
    options = {}
    cyrillic_to_latin = {
        'А': 'A', 'В': 'B', 'С': 'C', 'Д': 'D', 'Е': 'E', 'Ф': 'F', 'Г': 'G', 'Х': 'H', 'И': 'I', 'Й': 'J',
        'а': 'a', 'в': 'b', 'с': 'c', 'д': 'd', 'е': 'e', 'ф': 'f', 'г': 'g', 'х': 'h', 'и': 'i', 'й': 'j'
    }
    valid_letters = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]

    for line in lines[:10]:
        line = line.strip()
        if not line:
            continue

        if "." in line:
            parts = line.split(".", 1)
            if len(parts) == 2:
                letter = parts[0].strip().upper()
                text = parts[1].strip()
            else:
                continue
        else:
            if len(line) > 2 and line[1] == ' ':
                letter = line[0].upper()
                text = line[2:].strip()
            else:
                used_letters = set(options.keys())
                letter = None
                for available_letter in valid_letters:
                    if available_letter not in used_letters:
                        letter = available_letter
                        break

                if letter is None:
                    continue

                text = line

        if letter in cyrillic_to_latin:
            letter = cyrillic_to_latin[letter]

        if letter in valid_letters and text:
            options[letter] = text

    if len(options) < 2:
        await message.answer(
            "❌ Необходимо ввести минимум 2 варианта ответа. Попробуйте снова:"
        )
        return

    # Обновляем вопрос
    user_data = await state.get_data()
    questions = user_data.get("questions", [])
    question_num = user_data.get("editing_question_num", 1)

    if question_num <= len(questions):
        questions[question_num - 1]["options"] = options
        await state.update_data(questions=questions)

        await message.answer(
            f"✅ Варианты ответов для вопроса {question_num} обновлены!"
        )

        # Показываем выбор правильного ответа
        from common.manager_tests.keyboards import get_correct_answer_kb
        await message.answer(
            "Выберите новый правильный вариант ответа:",
            reply_markup=get_correct_answer_kb(options)
        )
        await state.set_state(states_group.edit_correct_answer)


async def edit_photo(callback: CallbackQuery, state: FSMContext, states_group, question_num: int):
    """Редактирование фото вопроса"""
    logger.info(f"Редактирование фото для вопроса {question_num}")

    user_data = await state.get_data()
    questions = user_data.get("questions", [])

    if question_num <= len(questions):
        current_question = questions[question_num - 1]
        has_photo = "photo_id" in current_question

        if has_photo:
            await callback.message.edit_text(
                f"📷 У вопроса {question_num} уже есть фото.\n\n"
                "Отправьте новое фото или удалите текущее:",
                reply_markup=get_photo_edit_kb()
            )
        else:
            await callback.message.edit_text(
                f"📷 Отправьте фото для вопроса {question_num}:"
            )

        await state.update_data(editing_question_num=question_num)
        await state.set_state(states_group.edit_question_photo)
    else:
        await callback.answer("❌ Вопрос не найден")


async def process_edit_photo(message: Message, state: FSMContext):
    """Обработка нового фото"""
    if not message.photo:
        await message.answer("❌ Пожалуйста, отправьте фото.")
        return

    photo = message.photo[-1]
    file_id = photo.file_id

    user_data = await state.get_data()
    questions = user_data.get("questions", [])
    question_num = user_data.get("editing_question_num", 1)

    if question_num <= len(questions):
        questions[question_num - 1]["photo_id"] = file_id
        await state.update_data(questions=questions)

        await message.answer(
            f"✅ Фото для вопроса {question_num} обновлено!"
        )

        # Возвращаемся к сводке
        await show_test_summary_with_edit(message, state)


# ==================== РЕГИСТРАЦИЯ ОБРАБОТЧИКОВ РЕДАКТИРОВАНИЯ ====================

def register_edit_handlers(router, states_group):
    """Регистрация всех обработчиков редактирования"""
    from aiogram import F
    from aiogram.filters import StateFilter

    # Обработчики редактирования названия теста
    @router.callback_query(F.data == "edit_test_name")
    async def handle_edit_test_name(callback: CallbackQuery, state: FSMContext):
        await edit_test_name(callback, state, states_group)

    @router.message(StateFilter(states_group.edit_test_name))
    async def handle_process_edit_test_name(message: Message, state: FSMContext):
        new_name = message.text.strip()

        if not new_name:
            await message.answer("❌ Название не может быть пустым. Попробуйте снова:")
            return

        await state.update_data(test_name=new_name)

        user_data = await state.get_data()
        course_name = user_data.get("course_name", "")
        subject_name = user_data.get("subject_name", "")
        lesson_name = user_data.get("lesson_name", "")

        info_text = (
            f"Курс: {course_name}\n"
            f"Предмет: {subject_name}\n"
            f"Урок: {lesson_name}\n"
            f"🏷 Название ДЗ: {new_name}\n\n"
        )

        from manager.keyboards.homework import get_step_edit_kb
        await message.answer(
            info_text + "✅ Название изменено! Хотите изменить еще раз или продолжить?",
            reply_markup=get_step_edit_kb("test_name", True)
        )
        # Возвращаемся к состоянию показа названия с кнопками редактирования
        await state.set_state(states_group.enter_test_name)

    # Обработчики редактирования текста вопроса
    @router.callback_query(F.data.startswith("edit_question_text_"))
    async def handle_edit_question_text(callback: CallbackQuery, state: FSMContext):
        question_num = int(callback.data.split("_")[-1])
        await edit_question_text(callback, state, states_group, question_num)

    @router.message(StateFilter(states_group.edit_question_text))
    async def handle_process_edit_question_text(message: Message, state: FSMContext):
        new_text = message.text.strip()

        if not new_text:
            await message.answer("❌ Текст вопроса не может быть пустым. Попробуйте снова:")
            return

        # Обновляем текущий вопрос
        user_data = await state.get_data()
        current_question = user_data.get("current_question", {})
        current_question["text"] = new_text
        await state.update_data(current_question=current_question)

        from manager.keyboards.homework import get_step_edit_kb
        await message.answer(
            f"📝 Текст вопроса:\n{new_text}\n\n✅ Текст изменен! Хотите изменить еще раз или продолжить?",
            reply_markup=get_step_edit_kb("question_text", True)
        )
        # Возвращаемся к состоянию показа текста с кнопками редактирования
        await state.set_state(states_group.enter_question_text)

    # Обработчики редактирования вариантов ответов
    @router.callback_query(F.data.startswith("edit_answer_options_"))
    async def handle_edit_answer_options(callback: CallbackQuery, state: FSMContext):
        question_num = int(callback.data.split("_")[-1])
        await edit_answer_options(callback, state, states_group, question_num)

    @router.message(StateFilter(states_group.edit_answer_options))
    async def handle_process_edit_answer_options(message: Message, state: FSMContext):
        # Используем ту же логику парсинга вариантов
        answer_text = message.text.strip()
        lines = answer_text.split("\n")

        if len(lines) < 2:
            await message.answer(
                "❌ Необходимо ввести минимум 2 варианта ответа.\n\n"
                "Поддерживаемые форматы:\n"
                "• A. Первый вариант\n"
                "• B Второй вариант\n"
                "• Третий вариант\n\n"
                "Попробуйте снова:"
            )
            return

        # Парсим варианты ответов
        options = {}
        cyrillic_to_latin = {
            'А': 'A', 'В': 'B', 'С': 'C', 'Д': 'D', 'Е': 'E', 'Ф': 'F', 'Г': 'G', 'Х': 'H', 'И': 'I', 'Й': 'J',
            'а': 'a', 'в': 'b', 'с': 'c', 'д': 'd', 'е': 'e', 'ф': 'f', 'г': 'g', 'х': 'h', 'и': 'i', 'й': 'j'
        }
        valid_letters = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]

        for line in lines[:10]:
            line = line.strip()
            if not line:
                continue

            if "." in line:
                parts = line.split(".", 1)
                if len(parts) == 2:
                    letter = parts[0].strip().upper()
                    text = parts[1].strip()
                else:
                    continue
            else:
                if len(line) > 2 and line[1] == ' ':
                    letter = line[0].upper()
                    text = line[2:].strip()
                else:
                    used_letters = set(options.keys())
                    letter = None
                    for available_letter in valid_letters:
                        if available_letter not in used_letters:
                            letter = available_letter
                            break

                    if letter is None:
                        continue

                    text = line

            if letter in cyrillic_to_latin:
                letter = cyrillic_to_latin[letter]

            if letter in valid_letters and text:
                options[letter] = text

        if len(options) < 2:
            await message.answer(
                "❌ Необходимо ввести минимум 2 варианта ответа. Попробуйте снова:"
            )
            return

        # Обновляем текущий вопрос
        user_data = await state.get_data()
        current_question = user_data.get("current_question", {})
        current_question["options"] = options
        await state.update_data(current_question=current_question)

        # Показываем варианты с возможностью редактирования
        options_text = ""
        for letter, text in sorted(options.items()):
            options_text += f"{letter}. {text}\n"

        from manager.keyboards.homework import get_step_edit_kb
        await message.answer(
            f"📝 Варианты ответов:\n{options_text}\n✅ Варианты изменены! Хотите изменить еще раз или продолжить?",
            reply_markup=get_step_edit_kb("answer_options", True)
        )
        # Возвращаемся к состоянию показа вариантов с кнопками редактирования
        await state.set_state(states_group.enter_answer_options)

    # Обработчики редактирования фото
    @router.callback_query(F.data.startswith("edit_question_photo_"))
    async def handle_edit_photo(callback: CallbackQuery, state: FSMContext):
        question_num = int(callback.data.split("_")[-1])
        await edit_photo(callback, state, states_group, question_num)

    @router.message(StateFilter(states_group.edit_question_photo))
    async def handle_process_edit_photo(message: Message, state: FSMContext):
        if not message.photo:
            await message.answer("❌ Пожалуйста, отправьте фото.")
            return

        photo = message.photo[-1]
        file_id = photo.file_id

        # Обновляем текущий вопрос
        user_data = await state.get_data()
        current_question = user_data.get("current_question", {})
        current_question["photo_id"] = file_id
        await state.update_data(current_question=current_question)

        from manager.keyboards.homework import get_step_edit_kb
        await message.answer_photo(
            photo=file_id,
            caption="📷 Фото изменено! Хотите изменить еще раз или продолжить?",
            reply_markup=get_step_edit_kb("photo", True)
        )
        # Возвращаемся к состоянию показа фото с кнопками редактирования
        await state.set_state(states_group.add_question_photo)

    # Обработчики управления фото
    @router.callback_query(F.data == "edit_photo")
    async def handle_request_new_photo(callback: CallbackQuery, state: FSMContext):
        # Проверяем, есть ли фото в сообщении
        if callback.message.photo:
            # Если есть фото, редактируем подпись
            await callback.message.edit_caption(
                caption="📷 Отправьте новое фото:"
            )
        else:
            # Если нет фото, редактируем текст
            await callback.message.edit_text("📷 Отправьте новое фото:")

        await state.set_state(states_group.edit_question_photo)

    @router.callback_query(F.data == "remove_photo")
    async def handle_remove_photo(callback: CallbackQuery, state: FSMContext):
        user_data = await state.get_data()
        current_question = user_data.get("current_question", {})

        if "photo_id" in current_question:
            del current_question["photo_id"]
            await state.update_data(current_question=current_question)

            # Отправляем новое сообщение без фото
            from manager.keyboards.homework import get_step_edit_kb
            await callback.message.answer(
                "✅ Фото удалено! Хотите добавить фото или продолжить?",
                reply_markup=get_step_edit_kb("photo", False)
            )
            # Удаляем старое сообщение с фото
            await callback.message.delete()
        else:
            await callback.answer("❌ У этого вопроса нет фото")

    @router.callback_query(F.data == "continue_without_edit")
    async def handle_continue_without_edit(callback: CallbackQuery, state: FSMContext):
        await show_test_summary_with_edit(callback, state)

    # Обработчик показа сводки с редактированием
    @router.callback_query(F.data == "edit_summary")
    async def handle_show_summary_edit(callback: CallbackQuery, state: FSMContext):
        await show_test_summary_with_edit(callback, state)

    # Обработчики продолжения для каждого шага
    @router.callback_query(F.data == "continue_test_name")
    async def handle_continue_test_name(callback: CallbackQuery, state: FSMContext):
        await callback.message.edit_text("Введите текст первого вопроса:")
        await state.set_state(states_group.enter_question_text)

    @router.callback_query(F.data == "continue_question_text")
    async def handle_continue_question_text(callback: CallbackQuery, state: FSMContext):
        await callback.message.edit_text(
            "Отправьте фото для этого вопроса (если нужно) или нажмите 'Пропустить':",
            reply_markup=get_photo_skip_kb()
        )
        await state.set_state(states_group.add_question_photo)

    @router.callback_query(F.data == "continue_photo")
    async def handle_continue_photo(callback: CallbackQuery, state: FSMContext):
        # Проверяем, есть ли фото в сообщении
        if callback.message.photo:
            # Если есть фото, отправляем новое сообщение
            await callback.message.answer("Введите номер микротемы:")
        else:
            # Если нет фото, редактируем текст
            await callback.message.edit_text("Введите номер микротемы:")
        await state.set_state(states_group.request_topic)

    @router.callback_query(F.data == "continue_answer_options")
    async def handle_continue_answer_options(callback: CallbackQuery, state: FSMContext):
        user_data = await state.get_data()
        current_question = user_data.get("current_question", {})
        options = current_question.get("options", {})

        await callback.message.edit_text(
            "Выберите правильный вариант ответа:",
            reply_markup=get_correct_answer_kb(options)
        )
        await state.set_state(states_group.select_correct_answer)

    @router.callback_query(F.data == "continue_summary")
    async def handle_continue_summary(callback: CallbackQuery, state: FSMContext):
        await confirm_test(callback, state)

    # Обработчики редактирования для каждого шага (без фильтра состояния)
    @router.callback_query(F.data == "edit_test_name")
    async def handle_edit_test_name_step(callback: CallbackQuery, state: FSMContext):
        user_data = await state.get_data()
        current_name = user_data.get("test_name", "")

        await callback.message.edit_text(
            f"📝 Текущее название ДЗ: {current_name}\n\n"
            "Введите новое название домашнего задания:"
        )
        await state.set_state(states_group.edit_test_name)

    @router.callback_query(F.data == "edit_question_text")
    async def handle_edit_question_text_step(callback: CallbackQuery, state: FSMContext):
        user_data = await state.get_data()
        current_question = user_data.get("current_question", {})
        current_text = current_question.get("text", "")

        await callback.message.edit_text(
            f"📝 Текущий текст вопроса:\n\n{current_text}\n\n"
            "Введите новый текст вопроса:"
        )
        await state.set_state(states_group.edit_question_text)

    @router.callback_query(F.data == "edit_photo")
    async def handle_edit_photo_step(callback: CallbackQuery, state: FSMContext):
        user_data = await state.get_data()
        current_question = user_data.get("current_question", {})
        has_photo = "photo_id" in current_question

        if has_photo:
            # Если есть фото в сообщении, редактируем подпись
            if callback.message.photo:
                await callback.message.edit_caption(
                    caption="📷 Отправьте новое фото или удалите текущее:",
                    reply_markup=get_photo_edit_kb()
                )
            else:
                await callback.message.edit_text(
                    "📷 Отправьте новое фото или удалите текущее:",
                    reply_markup=get_photo_edit_kb()
                )
        else:
            await callback.message.edit_text("📷 Отправьте фото для вопроса:")
        await state.set_state(states_group.edit_question_photo)

    @router.callback_query(F.data == "edit_answer_options")
    async def handle_edit_answer_options_step(callback: CallbackQuery, state: FSMContext):
        user_data = await state.get_data()
        current_question = user_data.get("current_question", {})
        current_options = current_question.get("options", {})

        options_text = ""
        for letter, text in sorted(current_options.items()):
            options_text += f"{letter}. {text}\n"

        await callback.message.edit_text(
            f"📝 Текущие варианты ответов:\n\n{options_text}\n"
            "Введите новые варианты ответа (от 2 до 10), каждый с новой строки.\n\n"
            "Поддерживаемые форматы:\n"
            "• A. Первый вариант\n"
            "• B Второй вариант\n"
            "• Третий вариант\n"
            "• Четвертый вариант"
        )
        await state.set_state(states_group.edit_answer_options)

