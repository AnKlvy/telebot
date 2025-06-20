"""
Регистратор обработчиков для quiz системы
Выносит общую логику отображения вопросов, обработки ответов и таймеров
"""

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
from typing import Dict, Set, Callable, Optional, Any

from database import (
    QuestionRepository, AnswerOptionRepository, BonusAnswerOptionRepository
)

# Глобальный словарь для отслеживания активных вопросов
# Структура: {question_uuid: {"chat_id": int, "state": FSMContext, "bot": Bot, "answered": bool}}
active_questions: Dict[str, Dict] = {}

# Множество для отслеживания завершенных вопросов (для избежания дублирования)
completed_questions: Set[str] = set()


def register_quiz_handlers(
    router: Router,
    test_state: State,
    poll_answer_handler: Optional[Callable] = None,
    timeout_handler: Optional[Callable] = None,
    finish_handler: Optional[Callable] = None
):
    """
    Регистрирует общие обработчики для quiz системы
    
    Args:
        router: Router для регистрации обработчиков
        test_state: Состояние FSM во время прохождения теста
        poll_answer_handler: Кастомный обработчик ответов (опционально)
        timeout_handler: Кастомный обработчик таймаута (опционально)
        finish_handler: Кастомный обработчик завершения теста (опционально)
    """
    
    @router.poll_answer(test_state)
    async def handle_quiz_poll_answer(poll: PollAnswer, state: FSMContext):
        """Универсальный обработчик ответа на вопрос"""


        try:
            data = await state.get_data()
            current_question_uuid = data.get("current_question_uuid")
        except Exception as e:
            logging.error(f"❌ QUIZ: Ошибка получения данных состояния: {e}")
            await poll.bot.send_message(
                poll.user.id,
                "❌ Ошибка обработки ответа. Пожалуйста, начните тест заново."
            )
            return
        
        if not current_question_uuid or current_question_uuid not in active_questions:


            # Проверяем, есть ли данные состояния
            current_state = await state.get_state()
            if current_state and data:
                # Отправляем сообщение пользователю о том, что тест был прерван
                try:
                    await poll.bot.send_message(
                        poll.user.id,
                        "❌ Тест был прерван из-за перезагрузки системы.\n"
                        "Пожалуйста, начните тест заново из меню."
                    )
                    # Очищаем состояние
                    await state.clear()

                except Exception as e:
                    logging.error(f"❌ QUIZ: Ошибка при отправке сообщения о прерванном тесте: {e}")

            return
        
        # Отмечаем вопрос как отвеченный
        active_questions[current_question_uuid]["answered"] = True

        
        # Если есть кастомный обработчик, вызываем его
        if poll_answer_handler:
            await poll_answer_handler(poll, state, current_question_uuid)
        else:
            # Стандартная обработка ответа
            await default_poll_answer_handler(poll, state, current_question_uuid)
    
    @router.poll(test_state)
    async def handle_quiz_poll_closed(poll: Poll, state: FSMContext, bot: Bot):
        """Резервный обработчик закрытия опроса"""

        
        try:
            data = await state.get_data()
            current_state = await state.get_state()
            current_question_uuid = data.get("current_question_uuid")
            
            if current_state != test_state:

                return
            
            # Проверяем, был ли уже дан ответ
            question_answered = data.get("question_answered", False)
            if question_answered:

                return
            
            # Проверяем активность основного таймера
            if current_question_uuid:
                if current_question_uuid in active_questions:

                    return
                
                if current_question_uuid in completed_questions:

                    return
            

            
            # Если есть кастомный обработчик таймаута, вызываем его
            if timeout_handler:
                await timeout_handler(poll, state, bot, current_question_uuid)
            else:
                # Стандартная обработка таймаута
                await default_timeout_handler(poll, state, bot, current_question_uuid)
                
        except Exception as e:
            logging.error(f"❌ QUIZ: Ошибка в резервном обработчике опроса: {e}")


async def send_next_question(chat_id: int, state: FSMContext, bot: Bot, finish_callback: Optional[Callable] = None):
    """Универсальная функция отправки следующего вопроса"""
    data = await state.get_data()
    index = data.get("q_index", 0)
    questions = data.get("questions", [])

    # Проверяем валидность данных состояния
    if not data or not questions:

        await bot.send_message(
            chat_id,
            "❌ Данные теста потеряны. Пожалуйста, начните тест заново из меню."
        )
        await state.clear()
        return

    if index >= len(questions):
        # Завершаем тест
        if finish_callback:
            await finish_callback(chat_id, state, bot)
        return
    
    question_data = questions[index]
    question_id = question_data['id']
    
    # Определяем тип теста и получаем варианты ответов
    # Проверяем, есть ли в данных состояния информация о бонусном тесте
    is_bonus_test = data.get("bonus_test_id") is not None



    if is_bonus_test:
        # Для бонусных тестов используем BonusAnswerOptionRepository
        answer_options = await BonusAnswerOptionRepository.get_by_bonus_question(question_id)

    else:
        # Для обычных тестов используем AnswerOptionRepository
        answer_options = await AnswerOptionRepository.get_by_question(question_id)


    if not answer_options:
        error_msg = f"❌ QUIZ: Варианты ответов не найдены для вопроса ID {question_id}"
        logging.error(error_msg)

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
        error_msg = f"❌ QUIZ: Правильный ответ не найден для вопроса ID {question_id}"
        logging.error(error_msg)

        await bot.send_message(chat_id, "❌ Ошибка: правильный ответ не найден")
        return
    
    # Генерируем уникальный ID для этого вопроса
    question_uuid = str(uuid.uuid4())
    
    # Сохраняем информацию о текущем вопросе
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
        question_answered=False
    )
    
    # Регистрируем активный вопрос
    active_questions[question_uuid] = {
        "chat_id": chat_id,
        "state": state,
        "bot": bot,
        "answered": False,
        "question_id": question_id,
        "start_time": datetime.now(),
        "finish_callback": finish_callback
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
    
    # Сохраняем ID сообщения с опросом
    await state.update_data(
        current_poll_message_id=poll_message.message_id,
        messages_to_delete=messages_to_delete
    )
    

    
    # Запускаем надежный таймер для обработки таймаута
    asyncio.create_task(handle_question_timeout_reliable(
        question_uuid, question_data['time_limit'], finish_callback
    ))


async def default_poll_answer_handler(poll: PollAnswer, state: FSMContext, question_uuid: str):
    """Стандартный обработчик ответа на вопрос"""
    data = await state.get_data()
    index = data.get("q_index", 0)
    questions = data.get("questions", [])
    current_question_id = data.get("current_question_id")
    current_answer_options = data.get("current_answer_options", [])
    question_start_time_str = data.get("question_start_time")
    
    if index >= len(questions) or not current_question_id:
        return
    
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
    
    # Отмечаем, что на вопрос ответили
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
    


    # Получаем finish_callback из активного вопроса
    finish_callback = None
    if question_uuid in active_questions:
        finish_callback = active_questions[question_uuid].get("finish_callback")

    # Отправляем следующий вопрос
    await send_next_question(poll.user.id, state, poll.bot, finish_callback)


async def default_timeout_handler(poll: Poll, state: FSMContext, bot: Bot, question_uuid: str):
    """Стандартный обработчик таймаута"""

    
    data = await state.get_data()
    user_id = data.get("user_id")
    if not user_id:
        logging.error("❌ QUIZ: Нет user_id в данных состояния")
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
        # Получаем finish_callback из активного вопроса (если есть)
        finish_callback = None
        if question_uuid and question_uuid in active_questions:
            finish_callback = active_questions[question_uuid].get("finish_callback")
        await send_next_question(user_id, state, bot, finish_callback)


async def handle_question_timeout_reliable(question_uuid: str, timeout_seconds: int, finish_callback: Optional[Callable] = None):
    """Надежная обработка таймаута вопроса через уникальный UUID"""
    try:

        await asyncio.sleep(timeout_seconds)
        
        # Проверяем, что вопрос еще активен
        if question_uuid not in active_questions:

            return
        
        question_info = active_questions[question_uuid]
        
        # Проверяем, был ли уже дан ответ
        if question_info["answered"]:

            del active_questions[question_uuid]
            return
        

        
        # Обрабатываем таймаут
        await process_question_timeout_reliable(question_uuid, finish_callback)
        
    except Exception as e:
        logging.error(f"❌ QUIZ: Ошибка в обработчике таймаута для {question_uuid}: {e}")
        if question_uuid in active_questions:
            del active_questions[question_uuid]


async def process_question_timeout_reliable(question_uuid: str, finish_callback: Optional[Callable] = None):
    """Надежная обработка таймаута вопроса"""
    try:
        if question_uuid not in active_questions:
            logging.error(f"❌ QUIZ: Вопрос {question_uuid} не найден в активных")
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



        if index >= len(questions) or not current_question_id:
            logging.error(f"❌ QUIZ: Некорректные данные вопроса для {question_uuid}")
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



        # Переходим к следующему вопросу
        await state.update_data(
            q_index=index + 1,
            question_results=question_results,
            question_answered=False
        )



        # Очищаем из активных вопросов
        del active_questions[question_uuid]

        # Небольшая задержка перед следующим вопросом
        await asyncio.sleep(2)

        # Отправляем следующий вопрос или завершаем тест
        await send_next_question(chat_id, state, bot, finish_callback)


    except Exception as e:
        logging.error(f"❌ QUIZ: Ошибка в process_question_timeout_reliable для {question_uuid}: {e}")
        import traceback


        # Очищаем из активных вопросов при ошибке
        if question_uuid in active_questions:
            del active_questions[question_uuid]


async def cleanup_test_messages(chat_id: int, data: dict, bot: Bot):
    """Удаление всех сообщений теста"""
    import time
    start_time = time.time()

    try:
        messages_to_delete = data.get("messages_to_delete", [])

        if not messages_to_delete:

            return



        # Удаляем сообщения пакетами для ускорения
        deleted_count = 0
        batch_size = 10

        for i in range(0, len(messages_to_delete), batch_size):
            batch = messages_to_delete[i:i + batch_size]

            # Создаем задачи для параллельного удаления
            tasks = []
            for message_id in batch:
                task = asyncio.create_task(delete_message_safe(bot, chat_id, message_id))
                tasks.append(task)

            # Ждем завершения всех задач в пакете
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Подсчитываем успешные удаления
            for result in results:
                if result is True:
                    deleted_count += 1

            # Небольшая задержка между пакетами для избежания rate limit
            if i + batch_size < len(messages_to_delete):
                await asyncio.sleep(0.05)

        end_time = time.time()
        duration = end_time - start_time


    except Exception as e:
        logging.error(f"❌ QUIZ: Ошибка при удалении сообщений теста: {e}")


async def delete_message_safe(bot: Bot, chat_id: int, message_id: int) -> bool:
    """Безопасное удаление сообщения"""
    try:
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
        return True
    except Exception as e:
        logging.debug(f"QUIZ: Не удалось удалить сообщение {message_id}: {e}")
        return False


async def cleanup_orphaned_quiz_states():
    """Очистка зависших состояний quiz после перезагрузки системы"""
    try:
        # Очищаем все активные вопросы (они потеряли актуальность после перезагрузки)
        active_questions.clear()
        completed_questions.clear()

    except Exception as e:
        logging.error(f"❌ QUIZ: Ошибка при очистке зависших состояний: {e}")


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


        # Очищаем старые завершенные вопросы (оставляем только последние 100)
        if len(completed_questions) > 100:
            completed_list = list(completed_questions)
            completed_questions.clear()
            completed_questions.update(completed_list[-50:])


    except Exception as e:
        logging.error(f"❌ QUIZ: Ошибка при очистке данных теста: {e}")


def get_active_questions_count() -> int:
    """Получить количество активных вопросов (для мониторинга)"""
    return len(active_questions)


def get_completed_questions_count() -> int:
    """Получить количество завершенных вопросов (для мониторинга)"""
    return len(completed_questions)
