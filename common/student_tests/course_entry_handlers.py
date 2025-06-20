"""
Обработчики для входных тестов курса
"""
import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from .states import StudentTestsStates
from .keyboards import get_back_to_test_kb
from database.repositories.user_repository import UserRepository
from database.repositories.student_repository import StudentRepository
from database.repositories.subject_repository import SubjectRepository
from database.repositories.question_repository import QuestionRepository
from database.repositories.course_entry_test_result_repository import CourseEntryTestResultRepository
from common.quiz_registrator import send_next_question, cleanup_test_messages

# Настройка логгера
logger = logging.getLogger(__name__)

router = Router()


async def handle_course_entry_test_real(callback: CallbackQuery, state: FSMContext, subject_id: str):
    """Обработчик для входного теста курса с реальной БД"""
    telegram_id = callback.from_user.id
    logger.info(f"ВЫЗОВ: handle_course_entry_test_real, telegram_id={telegram_id}, subject_id={subject_id}")

    try:
        # Получаем пользователя и студента
        user = await UserRepository.get_by_telegram_id(telegram_id)
        if not user:
            await callback.message.edit_text(
                "❌ Пользователь не найден в системе",
                reply_markup=get_back_to_test_kb()
            )
            return

        student = await StudentRepository.get_by_user_id(user.id)
        if not student:
            await callback.message.edit_text(
                "❌ Студент не найден в системе",
                reply_markup=get_back_to_test_kb()
            )
            return

        # Получаем предмет по ID (теперь subject_id - это реальный ID из БД)
        try:
            subject_id_int = int(subject_id)
            subject = await SubjectRepository.get_by_id(subject_id_int)
        except (ValueError, TypeError):
            # Если subject_id не число, пытаемся найти по имени (для обратной совместимости)
            subject = await SubjectRepository.get_by_name(subject_id)
        if not subject:
            await callback.message.edit_text(
                f"❌ Предмет не найден",
                reply_markup=get_back_to_test_kb()
            )
            return

        # Проверяем, проходил ли студент уже этот тест
        has_taken = await CourseEntryTestResultRepository.has_student_taken_test(student.id, subject.id)

        if has_taken:
            # Если тест уже пройден, показываем результаты
            logger.info(f"ТЕСТ УЖЕ ПРОЙДЕН: показываем результаты из БД")
            test_result = await CourseEntryTestResultRepository.get_by_student_and_subject(student.id, subject.id)

            if test_result:
                await show_course_entry_test_results(callback, state, test_result)
            else:
                await callback.message.edit_text(
                    "❌ Ошибка при получении результатов теста",
                    reply_markup=get_back_to_test_kb()
                )
            return

        # Получаем вопросы для теста
        questions = await QuestionRepository.get_random_questions_for_course_entry_test(
            telegram_id, subject.id, max_questions=30
        )

        if not questions:
            await callback.message.edit_text(
                f"❌ Нет доступных вопросов по предмету '{subject.name}'\n"
                "Возможно, вы не записаны на курсы с этим предметом или в курсах нет домашних заданий.",
                reply_markup=get_back_to_test_kb()
            )
            return

        logger.info(f"НАЙДЕНО ВОПРОСОВ: {len(questions)} для предмета {subject.name}")

        # Переходим к подтверждению теста вместо прямого запуска
        await show_course_entry_test_confirmation(callback, state, questions, student.id, subject.id, subject.name)

    except Exception as e:
        logger.error(f"ОШИБКА в handle_course_entry_test_real: {e}")
        await callback.message.edit_text(
            "❌ Произошла ошибка при загрузке теста. Попробуйте позже.",
            reply_markup=get_back_to_test_kb()
        )


async def show_course_entry_test_confirmation(callback: CallbackQuery, state: FSMContext, questions, student_id: int, subject_id: int, subject_name: str):
    """Показать подтверждение для начала входного теста курса"""
    try:
        # Вычисляем среднее время на вопрос для отображения
        avg_time = sum(q.time_limit for q in questions) // len(questions) if questions else 0

        text = (
            f"🎯 Входной тест курса\n\n"
            f"📚 Предмет: {subject_name}\n"
            f"📋 Вопросов: {len(questions)}\n"
            f"⏱ Среднее время на вопрос: {avg_time} секунд\n\n"
            f"ℹ️ Это входной тест для определения вашего уровня знаний по предмету.\n"
            f"Результат поможет адаптировать обучение под ваши потребности.\n\n"
            "Готовы начать?"
        )

        from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
        confirmation_kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="▶️ Начать тест", callback_data="start_course_entry_test")],
            *get_back_to_test_kb().inline_keyboard
        ])

        # Преобразуем объекты Question в словари для сериализации
        quiz_questions = []
        for question in questions:
            quiz_questions.append({
                'id': question.id,
                'text': question.text,
                'photo_path': question.photo_path,
                'time_limit': question.time_limit,
                'microtopic_number': question.microtopic_number,
                'answer_options': [
                    {
                        'id': opt.id,
                        'text': opt.text,
                        'is_correct': opt.is_correct,
                        'order_number': opt.order_number
                    }
                    for opt in question.answer_options
                ]
            })

        # Сохраняем данные для последующего запуска теста
        await state.update_data(
            test_type="course_entry",
            student_id=student_id,
            subject_id=subject_id,
            subject_name=subject_name,
            questions=quiz_questions,
            confirmation_message_id=callback.message.message_id
        )

        await callback.message.edit_text(text, reply_markup=confirmation_kb)
        await state.set_state(StudentTestsStates.course_entry_confirmation)

        logger.info(f"Показано подтверждение входного теста курса для предмета {subject_name}")

    except Exception as e:
        logger.error(f"Ошибка при показе подтверждения входного теста курса: {e}")
        await callback.message.edit_text(
            "❌ Произошла ошибка при подготовке теста. Попробуйте позже.",
            reply_markup=get_back_to_test_kb()
        )


# Обработчик кнопки "Начать тест" для входного теста курса
@router.callback_query(StudentTestsStates.course_entry_confirmation, F.data == "start_course_entry_test")
async def start_course_entry_test_confirmed(callback: CallbackQuery, state: FSMContext):
    """Запуск входного теста курса после подтверждения"""
    try:
        data = await state.get_data()
        questions = data.get("questions")
        student_id = data.get("student_id")
        subject_id = data.get("subject_id")
        subject_name = data.get("subject_name")

        if not all([questions, student_id, subject_id, subject_name]):
            logger.error("Отсутствуют данные для запуска теста")
            await callback.answer("❌ Ошибка: данные теста не найдены", show_alert=True)
            return

        # Запускаем тест
        await start_course_entry_test_with_quiz(callback, state, questions, student_id, subject_id, subject_name)

    except Exception as e:
        logger.error(f"Ошибка при запуске входного теста курса: {e}")
        await callback.message.edit_text(
            "❌ Произошла ошибка при запуске теста. Попробуйте позже.",
            reply_markup=get_back_to_test_kb()
        )


async def start_course_entry_test_with_quiz(callback: CallbackQuery, state: FSMContext, questions, student_id: int, subject_id: int, subject_name: str):
    """Запуск входного теста курса через quiz_registrator"""
    logger.info(f"ЗАПУСК ТЕСТА: {len(questions)} вопросов для студента {student_id}")

    # Проверяем, нужно ли преобразовывать вопросы (если они еще объекты Question)
    if questions and hasattr(questions[0], 'id'):
        # Это объекты Question, преобразуем их
        quiz_questions = []
        for question in questions:
            quiz_questions.append({
                'id': question.id,
                'text': question.text,
                'photo_path': question.photo_path,
                'time_limit': question.time_limit,
                'microtopic_number': question.microtopic_number,
                'answer_options': [
                    {
                        'id': opt.id,
                        'text': opt.text,
                        'is_correct': opt.is_correct,
                        'order_number': opt.order_number
                    }
                    for opt in question.answer_options
                ]
            })
    else:
        # Это уже словари, используем как есть
        quiz_questions = questions

    # Сохраняем данные теста в состоянии
    await state.update_data(
        test_type="course_entry",
        student_id=student_id,
        subject_id=subject_id,
        subject_name=subject_name,
        questions=quiz_questions,
        q_index=0,
        score=0,
        question_results=[]
    )

    # Функция завершения теста
    async def finish_course_entry_test(chat_id, state_inner, bot):
        await finish_course_entry_test_handler(chat_id, state_inner, bot)

    # ВАЖНО: Устанавливаем состояние ПЕРЕД запуском теста
    await state.set_state(StudentTestsStates.test_in_progress)

    # Запускаем первый вопрос
    await send_next_question(
        chat_id=callback.message.chat.id,
        state=state,
        bot=callback.bot,
        finish_callback=finish_course_entry_test
    )


async def finish_course_entry_test_handler(chat_id: int, state: FSMContext, bot):
    """Обработчик завершения входного теста курса"""
    data = await state.get_data()
    student_id = data.get("student_id")
    subject_id = data.get("subject_id")
    subject_name = data.get("subject_name")
    question_results = data.get("question_results", [])
    score = data.get("score", 0)

    logger.info(f"ЗАВЕРШЕНИЕ ТЕСТА: студент {student_id}, предмет {subject_id}, результатов {len(question_results)}")

    try:
        # Очищаем сообщения теста
        await cleanup_test_messages(chat_id, data, bot)

        # Сохраняем результаты в БД
        test_result = await CourseEntryTestResultRepository.create_test_result(
            student_id=student_id,
            subject_id=subject_id,
            question_results=question_results
        )

        logger.info(f"РЕЗУЛЬТАТ СОХРАНЕН: ID {test_result.id}, баллов {test_result.correct_answers}/{test_result.total_questions}")

        # Показываем результаты
        await show_course_entry_test_results_final(chat_id, state, test_result, bot)

    except Exception as e:
        logger.error(f"ОШИБКА при сохранении результатов: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")

        await bot.send_message(
            chat_id,
            "❌ Произошла ошибка при сохранении результатов теста. Попробуйте позже."
        )


async def show_course_entry_test_results(callback: CallbackQuery, state: FSMContext, test_result):
    """Показать результаты входного теста курса (для уже пройденного теста)"""
    from common.statistics import format_course_entry_test_result
    from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

    try:
        # Форматируем результаты
        result_text = await format_course_entry_test_result(test_result)

        # Создаем кнопки для детальной аналитики как у куратора
        buttons = [
            [InlineKeyboardButton(
                text="📊 Проценты по микротемам",
                callback_data=f"student_course_entry_detailed_{test_result.id}"
            )],
            [InlineKeyboardButton(
                text="💪 Сильные/слабые темы",
                callback_data=f"student_course_entry_summary_{test_result.id}"
            )]
        ]
        buttons.extend(get_back_to_test_kb().inline_keyboard)

        await callback.message.edit_text(
            result_text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
        )
        await state.set_state(StudentTestsStates.course_entry_result)

    except Exception as e:
        logger.error(f"ОШИБКА при показе результатов: {e}")
        await callback.message.edit_text(
            "❌ Ошибка при отображении результатов теста.",
            reply_markup=get_back_to_test_kb()
        )


async def show_course_entry_test_results_final(chat_id: int, state: FSMContext, test_result, bot):
    """Показать результаты входного теста курса после завершения"""
    from common.statistics import format_course_entry_test_result
    from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

    try:
        # Форматируем результаты
        result_text = await format_course_entry_test_result(test_result)

        # Создаем кнопки для детальной аналитики как у куратора
        buttons = [
            [InlineKeyboardButton(
                text="📊 Проценты по микротемам",
                callback_data=f"student_course_entry_detailed_{test_result.id}"
            )],
            [InlineKeyboardButton(
                text="💪 Сильные/слабые темы",
                callback_data=f"student_course_entry_summary_{test_result.id}"
            )]
        ]
        buttons.extend(get_back_to_test_kb().inline_keyboard)

        await bot.send_message(
            chat_id,
            result_text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
        )
        await state.set_state(StudentTestsStates.course_entry_result)

    except Exception as e:
        logger.error(f"ОШИБКА при показе результатов: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")

        await bot.send_message(
            chat_id,
            "❌ Ошибка при отображении результатов теста."
        )


# Функция для использования в transitions.py
async def handle_course_entry_confirmation(callback, state=None, user_role: str = None):
    """Обработчик состояния подтверждения входного теста курса для навигации"""
    from .base_handlers import show_course_entry_subjects
    await show_course_entry_subjects(callback, state)
