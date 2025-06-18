from aiogram import Router, F, Bot
from aiogram.types import Poll, PollAnswer, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.filters import Command, StateFilter
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from datetime import datetime, timedelta
import logging
import asyncio
import uuid
from typing import Dict, Set

from common.keyboards import get_main_menu_back_button
from common.utils import check_if_id_in_callback_data
from database import (
    HomeworkRepository, QuestionRepository, AnswerOptionRepository,
    HomeworkResultRepository, QuestionResultRepository, StudentRepository
)
from common.navigation import log
from student.handlers.homework import HomeworkStates

# Глобальный словарь для отслеживания активных вопросов
# Структура: {question_uuid: {"chat_id": int, "state": FSMContext, "bot": Bot, "answered": bool}}
active_questions: Dict[str, Dict] = {}

# Множество для отслеживания завершенных вопросов (для избежания дублирования)
completed_questions: Set[str] = set()

router = Router()


async def handle_test_back_navigation(callback: CallbackQuery, state: FSMContext):
    """Обработка возврата из состояния test_in_progress"""
    current_state = await state.get_state()
    logging.info(f"🔄 ФУНКЦИЯ: handle_test_back_navigation | ТЕКУЩЕЕ СОСТОЯНИЕ: {current_state}")

    await log("handle_test_back_navigation", "student", state)

    # Данные теста не очищаем, чтобы сохранить возможность повторного прохождения
    logging.info(f"🔄 Возврат из теста для пользователя {callback.from_user.id}")

    # Получаем данные о домашнем задании из состояния
    data = await state.get_data()
    homework_id = data.get("homework_id")

    logging.info(f"📊 ДАННЫЕ СОСТОЯНИЯ: homework_id={homework_id}, ключи={list(data.keys())}")

    if not homework_id:
        # Если нет данных о домашнем задании, возвращаемся к выбору
        logging.info("❌ Нет homework_id, возвращаемся к choose_homework")
        from student.handlers.homework import choose_homework
        await choose_homework(callback, state)
        return

    # Получаем информацию о домашнем задании
    homework = await HomeworkRepository.get_by_id(homework_id)
    if not homework:
        logging.error(f"Домашнее задание с ID {homework_id} не найдено в базе данных")
        await callback.answer("❌ Домашнее задание не найдено", show_alert=True)
        return

    # Получаем вопросы домашнего задания
    questions = await QuestionRepository.get_by_homework(homework_id)
    if not questions:
        await callback.answer("❌ В этом домашнем задании нет вопросов", show_alert=True)
        return

    # Вычисляем среднее время на вопрос для отображения
    avg_time = sum(q.time_limit for q in questions) // len(questions)

    text = (
        f"🔎 Урок: {homework.lesson.name}\n"
        f"📚 Предмет: {homework.subject.name}\n"
        f"📝 Домашнее задание: {homework.name}\n"
        f"📋 Вопросов: {len(questions)}\n"
        f"⏱ Среднее время на вопрос: {avg_time} секунд\n"
        f"  ⚠️ Баллы будут начислены только за 100% правильных ответов.\n"
        "Ты готов?"
    )

    confirmation_message = await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="▶️ Начать тест", callback_data="start_quiz")],
            *get_main_menu_back_button()
        ]
    ))

    # Сохраняем ID сообщения с подтверждением для последующего удаления
    await state.update_data(
        homework_id=homework_id,
        confirmation_message_id=confirmation_message.message_id
    )
    await state.set_state(HomeworkStates.confirmation)


@router.callback_query(HomeworkStates.repeat_test, F.data.startswith("homework_"))
async def repeat_homework_test(callback: CallbackQuery, state: FSMContext):
    """Повторное прохождение домашнего задания"""
    await log("repeat_homework_test", "student", state)
    logging.info(f"🔄 ПОВТОРНОЕ ПРОХОЖДЕНИЕ: callback_data: {callback.data}")

    data = await state.get_data()
    last_homework_id = data.get("last_homework_id")

    if last_homework_id:
        # Восстанавливаем данные для повторного прохождения
        homework_id = last_homework_id

        # Получаем данные домашнего задания для восстановления контекста
        homework = await HomeworkRepository.get_by_id(homework_id)
        if homework:
            await state.update_data(
                course_id=data.get("last_course_id"),
                subject_id=data.get("last_subject_id"),
                lesson_id=data.get("last_lesson_id"),
                homework_id=homework_id
            )
        else:
            await callback.answer("❌ Домашнее задание не найдено", show_alert=True)
            return
    else:
        await callback.answer("❌ Данные для повторного прохождения не найдены", show_alert=True)
        return

    logging.info(f"Студент повторно выбрал домашнее задание с ID: {homework_id}")

    # Переходим к подтверждению теста
    await show_homework_confirmation(callback, state, homework_id)


@router.callback_query(HomeworkStates.homework, F.data.startswith("homework_"))
async def confirm_test(callback: CallbackQuery, state: FSMContext):
    """Подтверждение начала домашнего задания"""
    await log("confirm_test", "student", state)
    logging.info(f"🔄 ОБРАБОТЧИК confirm_test вызван с callback_data: {callback.data}")

    homework_id = int(await check_if_id_in_callback_data("homework_", callback, state, "homework"))
    logging.info(f"Студент выбрал домашнее задание с ID: {homework_id}")

    # Переходим к подтверждению теста
    await show_homework_confirmation(callback, state, homework_id)


async def show_homework_confirmation(callback: CallbackQuery, state: FSMContext, homework_id: int):
    """Показ подтверждения для начала домашнего задания"""
    # Получаем информацию о домашнем задании
    homework = await HomeworkRepository.get_by_id(homework_id)
    if not homework:
        logging.error(f"Домашнее задание с ID {homework_id} не найдено в базе данных")
        await callback.answer("❌ Домашнее задание не найдено", show_alert=True)
        return

    logging.info(f"Найдено домашнее задание: {homework.name} (ID: {homework.id})")

    # Получаем вопросы домашнего задания
    questions = await QuestionRepository.get_by_homework(homework_id)

    if not questions:
        await callback.answer("❌ В этом домашнем задании нет вопросов", show_alert=True)
        return

    # Сохраняем информацию о домашнем задании в состоянии (только ID для избежания проблем с сериализацией)
    question_ids = [q.id for q in questions]
    await state.update_data(
        homework_id=homework_id,
        question_ids=question_ids
    )

    logging.info(f"Сохранены данные в состояние: homework_id={homework_id}, question_ids={question_ids}")

    # Вычисляем среднее время на вопрос для отображения
    avg_time = sum(q.time_limit for q in questions) // len(questions)

    text = (
        f"🔎 Урок: {homework.lesson.name}\n"
        f"📚 Предмет: {homework.subject.name}\n"
        f"📝 Домашнее задание: {homework.name}\n"
        f"📋 Вопросов: {len(questions)}\n"
        f"⏱ Среднее время на вопрос: {avg_time} секунд\n"
        f"  ⚠️ Баллы будут начислены только за 100% правильных ответов.\n"
        "Ты готов?"
    )

    confirmation_message = await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="▶️ Начать тест", callback_data="start_quiz")],
            *get_main_menu_back_button()
        ]
    ))

    # Сохраняем ID сообщения с подтверждением для последующего удаления
    await state.update_data(confirmation_message_id=confirmation_message.message_id)
    await state.set_state(HomeworkStates.confirmation)

@router.callback_query(HomeworkStates.confirmation, F.data == "start_quiz")
async def start_quiz(callback: CallbackQuery, state: FSMContext):
    """Начало прохождения домашнего задания"""
    await log("start_quiz", "student", state)

    data = await state.get_data()
    homework_id = data.get("homework_id")
    question_ids = data.get("question_ids", [])

    logging.info(f"Данные состояния при запуске теста: homework_id={homework_id}, question_ids={question_ids}")
    logging.info(f"Все данные состояния: {list(data.keys())}")

    if not homework_id or not question_ids:
        logging.error(f"Отсутствуют данные: homework_id={homework_id}, question_ids={question_ids}")
        await callback.answer("❌ Ошибка: данные домашнего задания не найдены", show_alert=True)
        return

    # Получаем данные заново из базы
    homework = await HomeworkRepository.get_by_id(homework_id)
    questions = await QuestionRepository.get_by_homework(homework_id)

    if not homework or not questions:
        logging.error(f"Не удалось получить данные из БД: homework={homework is not None}, questions={len(questions) if questions else 0}")
        await callback.answer("❌ Ошибка: данные домашнего задания не найдены", show_alert=True)
        return

    # Получаем ID студента
    student = await StudentRepository.get_by_telegram_id(callback.from_user.id)
    if not student:
        await callback.answer("❌ Студент не найден", show_alert=True)
        return

    # Проверяем, не проходил ли студент уже это домашнее задание
    existing_attempts = await HomeworkResultRepository.get_student_homework_attempts(student.id, homework_id)
    is_first_attempt = len(existing_attempts) == 0

    # Получаем ID сообщения с подтверждением из предыдущего состояния
    data = await state.get_data()
    confirmation_message_id = data.get("confirmation_message_id")

    # Инициализируем состояние теста
    messages_to_delete = []
    if confirmation_message_id:
        messages_to_delete.append(confirmation_message_id)

    await state.update_data(
        student_id=student.id,
        user_id=callback.from_user.id,  # Сохраняем для обработчика закрытия опроса
        score=0,
        q_index=0,
        total_questions=len(questions),
        is_first_attempt=is_first_attempt,
        question_results=[],
        start_time=datetime.now().isoformat(),
        messages_to_delete=messages_to_delete,  # Список сообщений для удаления после теста
        questions=[{
            'id': q.id,
            'text': q.text,
            'photo_path': q.photo_path,
            'time_limit': q.time_limit,
            'microtopic_number': q.microtopic_number
        } for q in questions],
        homework={
            'id': homework.id,
            'name': homework.name,
            'subject_name': homework.subject.name,
            'lesson_name': homework.lesson.name
        }
    )

    await state.set_state(HomeworkStates.test_in_progress)
    await callback.answer()
    await send_next_question(callback.message.chat.id, state, callback.bot)


async def send_next_question(chat_id, state: FSMContext, bot):
    """Отправка следующего вопроса"""
    data = await state.get_data()
    index = data.get("q_index", 0)
    questions = data.get("questions", [])

    if index >= len(questions):
        # Завершаем тест
        await finish_test(chat_id, state, bot)
        return

    question_data = questions[index]
    question_id = question_data['id']

    # Получаем варианты ответов для вопроса
    answer_options = await AnswerOptionRepository.get_by_question(question_id)
    if not answer_options:
        await bot.send_message(chat_id, "❌ Ошибка: варианты ответов не найдены")
        return

    # Сортируем варианты по порядковому номеру
    answer_options.sort(key=lambda x: x.order_number)

    # Формируем список вариантов ответов и находим правильный
    options = []
    correct_option_id = None

    for i, option in enumerate(answer_options):
        options.append(option.text)
        if option.is_correct:
            correct_option_id = i

    if correct_option_id is None:
        await bot.send_message(chat_id, "❌ Ошибка: правильный ответ не найден")
        return

    # Генерируем уникальный ID для этого вопроса
    question_uuid = str(uuid.uuid4())

    # Сохраняем информацию о текущем вопросе (сериализуемые данные)
    await state.update_data(
        current_question_id=question_id,
        current_question_uuid=question_uuid,
        current_answer_options=[{
            'id': opt.id,
            'text': opt.text,
            'is_correct': opt.is_correct,
            'order_number': opt.order_number
        } for opt in answer_options],
        question_start_time=datetime.now().isoformat(),
        question_answered=False  # Сбрасываем флаг для нового вопроса
    )

    # Регистрируем активный вопрос
    active_questions[question_uuid] = {
        "chat_id": chat_id,
        "state": state,
        "bot": bot,
        "answered": False,
        "question_id": question_id,
        "start_time": datetime.now()
    }

    # Используем индивидуальный таймер для каждого вопроса
    close_date = int((datetime.now() + timedelta(seconds=question_data['time_limit'])).timestamp())

    # Формируем текст вопроса
    question_text = question_data['text']
    photo_message = None

    if question_data['photo_path']:
        # Если есть фото, сначала отправляем его
        photo_message = await bot.send_photo(
            chat_id=chat_id,
            photo=question_data['photo_path'],
        )

    poll_message = await bot.send_poll(
        chat_id=chat_id,
        question=f"{question_text}",
        options=options,
        type="quiz",
        correct_option_id=correct_option_id,
        is_anonymous=False,
        close_date=close_date
    )

    # Сохраняем ID сообщений для последующего удаления
    data = await state.get_data()
    messages_to_delete = data.get("messages_to_delete", [])

    if photo_message:
        messages_to_delete.append(photo_message.message_id)
    messages_to_delete.append(poll_message.message_id)

    # Сохраняем ID сообщения с опросом для возможного принудительного закрытия
    await state.update_data(
        current_poll_message_id=poll_message.message_id,
        messages_to_delete=messages_to_delete
    )

    logging.info(f"📝 Отправлен вопрос {index + 1}/{len(questions)} | UUID: {question_uuid} | Таймер: {question_data['time_limit']}с")

    # Запускаем надежный таймер для обработки таймаута
    asyncio.create_task(handle_question_timeout_reliable(
        question_uuid, question_data['time_limit']
    ))



@router.poll_answer(HomeworkStates.test_in_progress)
async def handle_poll_answer(poll: PollAnswer, state: FSMContext):
    """Обработка ответа на вопрос"""
    await log("handle_poll_answer", "student", state)

    data = await state.get_data()
    index = data.get("q_index", 0)
    questions = data.get("questions", [])
    current_question_id = data.get("current_question_id")
    current_question_uuid = data.get("current_question_uuid")
    current_answer_options = data.get("current_answer_options", [])
    question_start_time_str = data.get("question_start_time")

    if index >= len(questions) or not current_question_id:
        return

    # Отмечаем вопрос как отвеченный в глобальном трекере
    if current_question_uuid and current_question_uuid in active_questions:
        active_questions[current_question_uuid]["answered"] = True
        logging.info(f"✅ Ответ получен для вопроса UUID: {current_question_uuid}")

    selected_option_index = poll.option_ids[0]
    selected_answer = current_answer_options[selected_option_index] if selected_option_index < len(current_answer_options) else None

    # Проверяем правильность ответа
    is_correct = selected_answer and selected_answer['is_correct']

    # Вычисляем время, потраченное на ответ
    time_spent = None
    if question_start_time_str:
        question_start_time = datetime.fromisoformat(question_start_time_str)
        time_spent = int((datetime.now() - question_start_time).total_seconds())

    # Получаем данные текущего вопроса
    current_question_data = questions[index]

    # Сохраняем результат ответа на вопрос
    question_results = data.get("question_results", [])
    question_results.append({
        "question_id": current_question_id,
        "selected_answer_id": selected_answer['id'] if selected_answer else None,
        "is_correct": is_correct,
        "time_spent": time_spent,
        "microtopic_number": current_question_data['microtopic_number']
    })

    # Отмечаем, что на вопрос ответили (чтобы избежать дублирования при закрытии опроса)
    await state.update_data(question_answered=True)

    # Обновляем счетчик правильных ответов
    score = data.get("score", 0)
    if is_correct:
        score += 1

    # Обновляем состояние
    await state.update_data(
        score=score,
        q_index=index + 1,
        question_results=question_results
    )

    logging.info(f"📊 Ответ обработан: {'✅ правильно' if is_correct else '❌ неправильно'} | Время: {time_spent}с")

    # Отправляем следующий вопрос
    await send_next_question(poll.user.id, state, poll.bot)


async def finish_test(chat_id, state: FSMContext, bot):
    """Завершение теста и сохранение результатов"""
    await log("finish_test", "student", state)

    data = await state.get_data()
    homework_id = data.get("homework_id")
    student_id = data.get("student_id")
    score = data.get("score", 0)
    total_questions = data.get("total_questions", 0)
    is_first_attempt = data.get("is_first_attempt", True)
    question_results = data.get("question_results", [])
    homework = data.get("homework")

    if not homework_id or not student_id:
        await bot.send_message(chat_id, "❌ Ошибка при сохранении результатов")
        return

    try:
        # Вычисляем баллы (3 балла за вопрос, только если 100% правильных ответов и первая попытка)
        points_earned = 0
        if score == total_questions and is_first_attempt:
            points_earned = total_questions * 3

        # Создаем результат домашнего задания
        homework_result = await HomeworkResultRepository.create(
            student_id=student_id,
            homework_id=homework_id,
            total_questions=total_questions,
            correct_answers=score,
            points_earned=points_earned,
            is_first_attempt=is_first_attempt
        )

        # Сохраняем результаты по каждому вопросу
        for result_data in question_results:
            await QuestionResultRepository.create(
                homework_result_id=homework_result.id,
                question_id=result_data["question_id"],
                selected_answer_id=result_data["selected_answer_id"],
                is_correct=result_data["is_correct"],
                time_spent=result_data["time_spent"],
                microtopic_number=result_data["microtopic_number"]
            )

        # Формируем сообщение с результатами
        percentage = round((score / total_questions) * 100, 1) if total_questions > 0 else 0

        if score == total_questions:
            result_emoji = "🎉"
            result_text = "Отлично! Все ответы правильные!"
            if is_first_attempt:
                result_text += f"\n💰 Получено баллов: {points_earned}"
            else:
                result_text += "\n🔄 Это повторная попытка, баллы не начисляются"
        elif percentage >= 80:
            result_emoji = "👏"
            result_text = "Хорошо! Почти все правильно!"
        elif percentage >= 60:
            result_emoji = "👍"
            result_text = "Неплохо! Есть над чем поработать"
        else:
            result_emoji = "📚"
            result_text = "Стоит повторить материал"

        message = (
            f"{result_emoji} Тест завершен!\n\n"
            f"📝 {homework['name']}\n"
            f"📚 {homework['subject_name']}\n"
            f"📊 Результат: {score}/{total_questions} ({percentage}%)\n"
            f"{result_text}\n\n"
            f"💡 Ты можешь пройти тест повторно для закрепления материала"
        )

        # Кнопки для дальнейших действий
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Пройти еще раз", callback_data=f"homework_{homework_id}")],
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main")]
        ])

        # Сохраняем данные для повторного прохождения ПЕРЕД отправкой сообщения
        await state.update_data(
            last_homework_id=homework_id,
            last_course_id=data.get("course_id"),
            last_subject_id=data.get("subject_id"),
            last_lesson_id=data.get("lesson_id")
        )

        # Устанавливаем состояние для повторного прохождения ПЕРЕД отправкой сообщения
        await state.set_state(HomeworkStates.repeat_test)

        await bot.send_message(chat_id, message, reply_markup=keyboard)

        # Удаляем все сообщения теста после небольшой задержки
        await asyncio.sleep(1)
        await cleanup_test_messages(chat_id, data, bot)

    except Exception as e:
        logging.error(f"Ошибка при сохранении результатов теста: {e}")
        await bot.send_message(chat_id, "❌ Ошибка при сохранении результатов. Попробуйте еще раз.")


async def handle_question_timeout_reliable(question_uuid: str, timeout_seconds: int):
    """Надежная обработка таймаута вопроса через уникальный UUID"""
    try:
        logging.info(f"⏰ Запущен таймер для вопроса UUID: {question_uuid} на {timeout_seconds} секунд")
        await asyncio.sleep(timeout_seconds)

        # Проверяем, что вопрос еще активен
        if question_uuid not in active_questions:
            logging.info(f"🔄 Вопрос {question_uuid} уже не активен, таймаут отменен")
            return

        question_info = active_questions[question_uuid]

        # Проверяем, был ли уже дан ответ
        if question_info["answered"]:
            logging.info(f"✅ На вопрос {question_uuid} уже ответили, таймаут отменен")
            # Очищаем из активных вопросов
            del active_questions[question_uuid]
            return

        # Проверяем, что состояние еще актуально
        state = question_info["state"]
        current_state = await state.get_state()

        if current_state != HomeworkStates.test_in_progress:
            logging.info(f"🔄 Состояние изменилось ({current_state}), таймаут отменен для {question_uuid}")
            del active_questions[question_uuid]
            return

        # Проверяем, что это все еще тот же вопрос в состоянии
        data = await state.get_data()
        current_question_uuid = data.get("current_question_uuid")

        if current_question_uuid != question_uuid:
            logging.info(f"🔄 Текущий вопрос изменился ({current_question_uuid}), таймаут отменен для {question_uuid}")
            del active_questions[question_uuid]
            return

        logging.info(f"⏰ ТАЙМАУТ! Обрабатываем истечение времени для вопроса {question_uuid}")

        # Обрабатываем таймаут
        await process_question_timeout_reliable(question_uuid)

    except Exception as e:
        logging.error(f"❌ Ошибка в обработчике таймаута для {question_uuid}: {e}")
        # Очищаем из активных вопросов при ошибке
        if question_uuid in active_questions:
            del active_questions[question_uuid]


async def process_question_timeout_reliable(question_uuid: str):
    """Надежная обработка таймаута вопроса"""
    try:
        if question_uuid not in active_questions:
            logging.error(f"❌ Вопрос {question_uuid} не найден в активных")
            return

        question_info = active_questions[question_uuid]
        chat_id = question_info["chat_id"]
        state = question_info["state"]
        bot = question_info["bot"]

        # Отмечаем как завершенный
        completed_questions.add(question_uuid)

        data = await state.get_data()
        index = data.get("q_index", 0)
        questions = data.get("questions", [])
        current_question_id = data.get("current_question_id")
        question_start_time_str = data.get("question_start_time")

        logging.info(f"⏰ Обработка таймаута: index={index}, question_id={current_question_id}")

        if index >= len(questions) or not current_question_id:
            logging.error(f"❌ Некорректные данные вопроса для {question_uuid}")
            del active_questions[question_uuid]
            return

        # Вычисляем время
        time_spent = None
        if question_start_time_str:
            question_start_time = datetime.fromisoformat(question_start_time_str)
            time_spent = int((datetime.now() - question_start_time).total_seconds())

        # Получаем данные текущего вопроса
        current_question_data = questions[index]

        # Сохраняем результат как неправильный ответ (таймаут)
        question_results = data.get("question_results", [])
        question_results.append({
            "question_id": current_question_id,
            "selected_answer_id": None,
            "is_correct": False,
            "time_spent": time_spent,
            "microtopic_number": current_question_data['microtopic_number']
        })

        # Показываем правильный ответ
        current_answer_options = data.get("current_answer_options", [])
        correct_answer = next((opt for opt in current_answer_options if opt['is_correct']), None)

        if correct_answer:
            timeout_message = await bot.send_message(
                chat_id,
                f"⏰ Время вышло!\n\n"
                f"✅ Правильный ответ: {correct_answer['text']}"
            )

            # Добавляем сообщение о таймауте в список для удаления
            data = await state.get_data()
            messages_to_delete = data.get("messages_to_delete", [])
            messages_to_delete.append(timeout_message.message_id)
            await state.update_data(messages_to_delete=messages_to_delete)

            logging.info(f"📤 Отправлено сообщение о таймауте пользователю {chat_id}")

        # Переходим к следующему вопросу
        await state.update_data(
            q_index=index + 1,
            question_results=question_results,
            question_answered=False  # Сбрасываем флаг
        )

        logging.info(f"➡️ Переход к следующему вопросу: {index + 1}")

        # Очищаем из активных вопросов
        del active_questions[question_uuid]

        # Небольшая задержка перед следующим вопросом
        await asyncio.sleep(2)

        # Отправляем следующий вопрос или завершаем тест
        await send_next_question(chat_id, state, bot)
        logging.info(f"✅ Обработка таймаута завершена для {question_uuid}")

    except Exception as e:
        logging.error(f"❌ Ошибка в process_question_timeout_reliable для {question_uuid}: {e}")
        import traceback
        logging.error(f"📋 Traceback: {traceback.format_exc()}")

        # Очищаем из активных вопросов при ошибке
        if question_uuid in active_questions:
            del active_questions[question_uuid]


@router.poll(HomeworkStates.test_in_progress)
async def handle_poll_closed(poll: Poll, state: FSMContext, bot: Bot):
    """Резервный обработчик закрытия опроса (на случай если основной таймер не сработает)"""
    logging.info(f"🔔 РЕЗЕРВНЫЙ обработчик: Poll closed event: poll_id={poll.id}, is_closed={poll.is_closed}")

    try:
        # Получаем данные состояния
        data = await state.get_data()
        current_state = await state.get_state()
        current_question_uuid = data.get("current_question_uuid")

        # Проверяем базовые условия
        if current_state != HomeworkStates.test_in_progress:
            logging.info(f"❌ Неправильное состояние: {current_state}")
            return

        # Проверяем, был ли уже дан ответ
        question_answered = data.get("question_answered", False)
        if question_answered:
            logging.info("✅ Ответ уже был дан, пропускаем резервную обработку")
            return

        # Проверяем, обрабатывается ли этот вопрос основным таймером
        if current_question_uuid:
            if current_question_uuid in active_questions:
                # Основной таймер еще активен, не вмешиваемся
                logging.info(f"🔄 Основной таймер активен для {current_question_uuid}, резервный обработчик пропускает")
                return

            if current_question_uuid in completed_questions:
                # Вопрос уже обработан основным таймером
                logging.info(f"✅ Вопрос {current_question_uuid} уже обработан основным таймером")
                return

        # Если дошли до сюда, значит основной таймер не сработал
        logging.warning(f"⚠️ РЕЗЕРВНАЯ ОБРАБОТКА ТАЙМАУТА для poll {poll.id}")

        # Используем упрощенную логику обработки таймаута
        user_id = data.get("user_id")
        if not user_id:
            logging.error("❌ Нет user_id в данных состояния")
            return

        # Показываем сообщение о таймауте
        current_answer_options = data.get("current_answer_options", [])
        correct_answer = next((opt for opt in current_answer_options if opt['is_correct']), None)

        if correct_answer:
            timeout_message = await bot.send_message(
                user_id,
                f"⏰ Время вышло! (резервная обработка)\n\n"
                f"✅ Правильный ответ: {correct_answer['text']}"
            )

            # Добавляем сообщение о таймауте в список для удаления
            messages_to_delete = data.get("messages_to_delete", [])
            messages_to_delete.append(timeout_message.message_id)
            await state.update_data(messages_to_delete=messages_to_delete)

        # Сохраняем результат таймаута
        index = data.get("q_index", 0)
        questions = data.get("questions", [])
        current_question_id = data.get("current_question_id")

        if index < len(questions) and current_question_id:
            current_question_data = questions[index]
            question_results = data.get("question_results", [])

            question_results.append({
                "question_id": current_question_id,
                "selected_answer_id": None,
                "is_correct": False,
                "time_spent": None,
                "microtopic_number": current_question_data['microtopic_number']
            })

            # Переходим к следующему вопросу
            await state.update_data(
                q_index=index + 1,
                question_results=question_results,
                question_answered=False
            )

            await asyncio.sleep(2)
            await send_next_question(user_id, state, bot)

        logging.info("✅ Резервная обработка таймаута завершена")

    except Exception as e:
        logging.error(f"❌ Ошибка в резервном обработчике опроса: {e}")
        import traceback
        logging.error(f"📋 Traceback: {traceback.format_exc()}")


async def cleanup_test_messages(chat_id: int, data: dict, bot: Bot):
    """Удаление всех сообщений теста"""
    try:
        messages_to_delete = data.get("messages_to_delete", [])

        if not messages_to_delete:
            logging.info("🧹 Нет сообщений для удаления")
            return

        deleted_count = 0
        for message_id in messages_to_delete:
            try:
                await bot.delete_message(chat_id=chat_id, message_id=message_id)
                deleted_count += 1
                # Небольшая задержка между удалениями, чтобы не превысить лимиты API
                await asyncio.sleep(0.1)
            except Exception as e:
                # Игнорируем ошибки удаления (сообщение могло быть уже удалено)
                logging.debug(f"Не удалось удалить сообщение {message_id}: {e}")

        logging.info(f"🧹 Удалено {deleted_count} сообщений теста для пользователя {chat_id}")

    except Exception as e:
        logging.error(f"❌ Ошибка при удалении сообщений теста: {e}")


async def cleanup_test_data(user_id: int):
    """Очистка данных завершенного теста"""
    try:
        # Очищаем активные вопросы для этого пользователя
        questions_to_remove = []
        for question_uuid, question_info in active_questions.items():
            if question_info.get("chat_id") == user_id:
                questions_to_remove.append(question_uuid)

        for question_uuid in questions_to_remove:
            del active_questions[question_uuid]
            logging.info(f"🧹 Очищен активный вопрос {question_uuid} для пользователя {user_id}")

        # Очищаем старые завершенные вопросы (оставляем только последние 100)
        if len(completed_questions) > 100:
            # Преобразуем в список, сортируем и оставляем последние
            completed_list = list(completed_questions)
            completed_questions.clear()
            completed_questions.update(completed_list[-50:])  # Оставляем последние 50
            logging.info("🧹 Очищены старые завершенные вопросы")

    except Exception as e:
        logging.error(f"❌ Ошибка при очистке данных теста: {e}")


def get_active_questions_count() -> int:
    """Получить количество активных вопросов (для мониторинга)"""
    return len(active_questions)


def get_completed_questions_count() -> int:
    """Получить количество завершенных вопросов (для мониторинга)"""
    return len(completed_questions)

