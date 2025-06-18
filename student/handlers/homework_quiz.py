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
from common.quiz_registrator import (
    register_quiz_handlers, send_next_question, cleanup_test_messages, cleanup_test_data
)
from database import (
    HomeworkRepository, QuestionRepository, AnswerOptionRepository,
    HomeworkResultRepository, QuestionResultRepository, StudentRepository
)
from common.navigation import log
from student.handlers.homework import HomeworkStates

router = Router()

# Регистрируем общие quiz обработчики
register_quiz_handlers(
    router=router,
    test_state=HomeworkStates.test_in_progress,
    poll_answer_handler=None,  # Используем стандартный обработчик
    timeout_handler=None,      # Используем стандартный обработчик
    finish_handler=None        # Будем передавать в send_next_question
)


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

        # Проверяем, были ли уже начислены баллы за это ДЗ
    points_already_awarded = await HomeworkResultRepository.has_points_awarded(student.id, homework_id)

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
        points_already_awarded=points_already_awarded,
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
    await send_next_question(callback.message.chat.id, state, callback.bot, finish_test)





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
        # Вычисляем баллы (3 балла за вопрос, только если 100% правильных ответов и баллы еще не начислялись)
        points_earned = 0
        points_awarded = False
        if score == total_questions and not data.get("points_already_awarded", False):
            points_earned = total_questions * 3
            points_awarded = True

        # Создаем результат домашнего задания
        homework_result = await HomeworkResultRepository.create(
            student_id=student_id,
            homework_id=homework_id,
            total_questions=total_questions,
            correct_answers=score,
            points_earned=points_earned,
            is_first_attempt=is_first_attempt,
            points_awarded=points_awarded
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

        # Обновляем баллы и уровень студента в таблице students
        if points_awarded:
            await StudentRepository.update_points_and_level(student_id)
            logging.info(f"✅ Обновлены баллы студента {student_id}: +{points_earned} баллов")

        # Формируем сообщение с результатами
        percentage = round((score / total_questions) * 100, 1) if total_questions > 0 else 0

        if score == total_questions:
            result_emoji = "🎉"
            result_text = "Отлично! Все ответы правильные!"
            if points_awarded:
                result_text += f"\n💰 Получено баллов: {points_earned}"
            else:
                result_text += "\n🔄 Баллы уже были начислены ранее"
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







