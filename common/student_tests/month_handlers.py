"""
Обработчики для тестов месяца (входные и контрольные)
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
from database.repositories.month_test_repository import MonthTestRepository
from database.repositories.month_entry_test_result_repository import MonthEntryTestResultRepository
from database.repositories.month_control_test_result_repository import MonthControlTestResultRepository
from database.repositories.microtopic_repository import MicrotopicRepository
from database.repositories.question_repository import QuestionRepository
from common.quiz_registrator import send_next_question, cleanup_test_messages
import random

# Настройка логгера
logger = logging.getLogger(__name__)

router = Router()


async def generate_month_test_questions(month_test_id: int):
    """Генерирует вопросы для теста месяца на основе микротем"""
    try:
        # Получаем тест месяца
        month_test = await MonthTestRepository.get_by_id(month_test_id)
        if not month_test:
            logger.error(f"Тест месяца с ID {month_test_id} не найден")
            return []

        # Получаем связи микротем с тестом месяца
        month_test_microtopics = month_test.microtopics

        if not month_test_microtopics:
            logger.error(f"У теста месяца {month_test_id} нет микротем")
            return []

        # Получаем объекты микротем по номерам
        microtopic_numbers = [mtm.microtopic_number for mtm in month_test_microtopics]
        microtopics = await MicrotopicRepository.get_by_subject(month_test.subject_id)
        test_microtopics = [mt for mt in microtopics if mt.number in microtopic_numbers]

        if not test_microtopics:
            logger.error(f"Не найдены микротемы для теста месяца {month_test_id}")
            return []

        all_questions = []

        # Для каждой микротемы берем 3 случайных вопроса из домашних заданий
        for microtopic in test_microtopics:
            questions = await QuestionRepository.get_random_questions_by_microtopic(
                microtopic_number=microtopic.number,
                subject_id=month_test.subject_id,
                limit=3
            )
            all_questions.extend(questions)

        if not all_questions:
            logger.error(f"Не найдено вопросов для теста месяца {month_test_id}")
            return []

        # Перемешиваем вопросы
        random.shuffle(all_questions)
        
        # Подготавливаем данные для quiz_registrator
        quiz_questions = []
        for question in all_questions:
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

        logger.info(f"Сгенерировано {len(quiz_questions)} вопросов для теста месяца {month_test_id}")
        return quiz_questions

    except Exception as e:
        logger.error(f"Ошибка при генерации вопросов для теста месяца: {e}")
        return []


async def show_month_entry_test_confirmation(callback: CallbackQuery, state: FSMContext, test_questions, student_id: int, month_test):
    """Показать подтверждение для начала входного теста месяца"""
    try:
        # Вычисляем среднее время на вопрос для отображения
        avg_time = sum(q.get('time_limit', 60) for q in test_questions) // len(test_questions) if test_questions else 60

        # Получаем информацию о микротемах
        microtopic_numbers = [mtm.microtopic_number for mtm in month_test.microtopics]
        microtopics = await MicrotopicRepository.get_by_subject(month_test.subject_id)
        test_microtopics = [mt for mt in microtopics if mt.number in microtopic_numbers]

        microtopic_names = ", ".join([mt.name for mt in test_microtopics[:3]])  # Показываем первые 3
        if len(test_microtopics) > 3:
            microtopic_names += f" и еще {len(test_microtopics) - 3}"

        text = (
            f"📅 Входной тест месяца\n\n"
            f"📚 Предмет: {month_test.subject.name}\n"
            f"📝 Тест: {month_test.name}\n"
            f"📋 Вопросов: {len(test_questions)}\n"
            f"⏱ Среднее время на вопрос: {avg_time} секунд\n"
            f"🎯 Микротемы: {microtopic_names}\n\n"
            f"ℹ️ Это входной тест для оценки ваших знаний по темам месяца.\n"
            f"По каждой микротеме будет до 3 вопросов (в зависимости от доступности).\n\n"
            "Готовы начать?"
        )

        from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
        confirmation_kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="▶️ Начать тест", callback_data="start_month_entry_test")],
            *get_back_to_test_kb().inline_keyboard
        ])

        # Сохраняем данные для последующего запуска теста (только сериализуемые данные)
        await state.update_data(
            month_test_id=month_test.id,
            student_id=student_id,
            questions=test_questions,  # test_questions уже словари из generate_month_test_questions
            confirmation_message_id=callback.message.message_id
        )

        await callback.message.edit_text(text, reply_markup=confirmation_kb)
        await state.set_state(StudentTestsStates.month_entry_confirmation)

        logger.info(f"Показано подтверждение входного теста месяца для теста {month_test.name}")

    except Exception as e:
        logger.error(f"Ошибка при показе подтверждения входного теста месяца: {e}")
        await callback.message.edit_text(
            "❌ Произошла ошибка при подготовке теста. Попробуйте позже.",
            reply_markup=get_back_to_test_kb()
        )


async def show_month_control_test_confirmation(callback: CallbackQuery, state: FSMContext, test_questions, student_id: int, month_test):
    """Показать подтверждение для начала контрольного теста месяца"""
    try:
        # Вычисляем среднее время на вопрос для отображения
        avg_time = sum(q.get('time_limit', 60) for q in test_questions) // len(test_questions) if test_questions else 60

        # Получаем информацию о микротемах
        microtopic_numbers = [mtm.microtopic_number for mtm in month_test.microtopics]

        microtopics = await MicrotopicRepository.get_by_subject(month_test.subject_id)
        test_microtopics = [mt for mt in microtopics if mt.number in microtopic_numbers]

        microtopic_names = ", ".join([mt.name for mt in test_microtopics[:3]])  # Показываем первые 3
        if len(test_microtopics) > 3:
            microtopic_names += f" и еще {len(test_microtopics) - 3}"

        text = (
            f"🎯 Контрольный тест месяца\n\n"
            f"📚 Предмет: {month_test.subject.name}\n"
            f"📝 Тест: {month_test.name}\n"
            f"📋 Вопросов: {len(test_questions)}\n"
            f"⏱ Среднее время на вопрос: {avg_time} секунд\n"
            f"🎯 Микротемы: {microtopic_names}\n\n"
            f"ℹ️ Это контрольный тест для проверки прогресса по темам месяца.\n"
            f"Результат будет сравнен с входным тестом.\n\n"
            "Готовы начать?"
        )

        from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
        confirmation_kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="▶️ Начать тест", callback_data="start_month_control_test")],
            *get_back_to_test_kb().inline_keyboard
        ])

        # Сохраняем данные для последующего запуска теста (только сериализуемые данные)
        await state.update_data(
            month_test_id=month_test.id,
            student_id=student_id,
            questions=test_questions,  # test_questions уже словари из generate_month_test_questions
            confirmation_message_id=callback.message.message_id
        )

        await callback.message.edit_text(text, reply_markup=confirmation_kb)
        await state.set_state(StudentTestsStates.month_control_confirmation)

        logger.info(f"Показано подтверждение контрольного теста месяца для теста {month_test.name}")

    except Exception as e:
        logger.error(f"Ошибка при показе подтверждения контрольного теста месяца: {e}")
        await callback.message.edit_text(
            "❌ Произошла ошибка при подготовке теста. Попробуйте позже.",
            reply_markup=get_back_to_test_kb()
        )


async def finish_month_entry_test(chat_id: int, state: FSMContext, bot):
    """Завершение входного теста месяца и сохранение результатов в БД"""
    try:
        data = await state.get_data()
        question_results = data.get("question_results", [])
        month_test_id = data.get("month_test_id")
        student_id = data.get("student_id")

        if not month_test_id or not student_id:
            logger.error("Нет данных о тесте или студенте")
            await bot.send_message(
                chat_id,
                "❌ Ошибка: данные теста не найдены",
                reply_markup=get_back_to_test_kb()
            )
            return

        # Сохраняем результат теста в БД
        test_result = await MonthEntryTestResultRepository.create_test_result(
            student_id=student_id,
            month_test_id=month_test_id,
            question_results=question_results
        )


        month_test = await MonthTestRepository.get_by_id(month_test_id)

        # Формируем текст результата
        result_text = f"📊 Входной тест месяца завершен!\n\n"
        result_text += f"📗 {month_test.subject.name}:\n"
        result_text += f"Тест: {month_test.name}\n"
        result_text += f"Верных: {test_result.correct_answers} / {test_result.total_questions}\n"
        result_text += f"Процент: {test_result.score_percentage}%\n\n"


        # Очищаем сообщения теста
        await cleanup_test_messages(chat_id, data, bot)

        await bot.send_message(
            chat_id,
            result_text,
            reply_markup=get_back_to_test_kb()
        )
        await state.set_state(StudentTestsStates.month_entry_result)

        logger.info(f"Тест месяца завершен: студент {student_id}, результат {test_result.score_percentage}%")

    except Exception as e:
        logger.error(f"Ошибка при завершении теста месяца: {e}")
        await bot.send_message(
            chat_id,
            "❌ Ошибка при сохранении результатов теста",
            reply_markup=get_back_to_test_kb()
        )


async def finish_month_control_test(chat_id: int, state: FSMContext, bot):
    """Завершение контрольного теста месяца и сохранение результатов в БД"""
    try:
        data = await state.get_data()
        question_results = data.get("question_results", [])
        month_test_id = data.get("month_test_id")
        student_id = data.get("student_id")

        if not month_test_id or not student_id:
            logger.error("Нет данных о тесте или студенте")
            await bot.send_message(
                chat_id,
                "❌ Ошибка: данные теста не найдены",
                reply_markup=get_back_to_test_kb()
            )
            return

        # Сохраняем результат теста в БД
        test_result = await MonthControlTestResultRepository.create_test_result(
            student_id=student_id,
            month_test_id=month_test_id,
            question_results=question_results
        )

        # Показываем статистику
        await show_month_control_test_statistics_final(chat_id, state, test_result, bot)

        logger.info(f"Контрольный тест месяца завершен для студента {test_result.student_id}")

    except Exception as e:
        logger.error(f"Ошибка при завершении контрольного теста месяца: {e}")
        await bot.send_message(
            chat_id,
            "❌ Ошибка при сохранении результатов теста",
            reply_markup=get_back_to_test_kb()
        )


async def show_month_control_test_statistics_final(chat_id: int, state: FSMContext, test_result, bot):
    """Показать статистику контрольного теста месяца после завершения"""
    try:
        # Получаем тест месяца отдельно (объект test_result отвязан от сессии)
        month_test = await MonthTestRepository.get_by_id(test_result.month_test_id)
        if not month_test:
            logger.error(f"Тест месяца с ID {test_result.month_test_id} не найден")
            return

        # Пытаемся найти соответствующий входной результат для сравнения
        comparison_text = ""
        entry_result = await MonthEntryTestResultRepository.get_by_student_and_month_test(
            test_result.student_id, test_result.month_test_id
        )
        if entry_result:
            # Показываем сравнение с входным тестом
            comparison_text = f"\n📊 Сравнение с входным тестом:\n"
            comparison_text += f"Верных: {entry_result.correct_answers}/{entry_result.total_questions} → {test_result.correct_answers}/{test_result.total_questions}\n"

            # Рассчитываем общий рост
            if entry_result.score_percentage > 0:
                growth = ((test_result.score_percentage - entry_result.score_percentage) / entry_result.score_percentage) * 100
                if growth > 0:
                    comparison_text += f"📈 Общий рост: +{growth:.1f}%\n"
                elif growth < 0:
                    comparison_text += f"📉 Общее снижение: {growth:.1f}%\n"
                else:
                    comparison_text += f"📊 Результат остался на том же уровне\n"
            else:
                if test_result.score_percentage > 0:
                    comparison_text += f"📈 Рост: +{test_result.score_percentage:.1f} п.п.\n"

        # Формируем результат
        result_text = f"🎉 Контрольный тест месяца завершен!\n\n"
        result_text += f"📗 {month_test.subject.name}\n"
        result_text += f"Тест: {month_test.name}\n"
        result_text += f"Верных ответов: {test_result.correct_answers} / {test_result.total_questions}\n"
        result_text += f"Процент: {test_result.score_percentage}%\n"
        result_text += comparison_text


        result_text += "\nВыберите тип аналитики:"

        # Создаем кнопки для детальной аналитики (как у куратора)
        from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
        buttons = [
            [InlineKeyboardButton(
                text="📊 Проценты по микротемам",
                callback_data=f"student_month_control_detailed_{test_result.id}"
            )],
            [InlineKeyboardButton(
                text="💪 Сильные/слабые темы",
                callback_data=f"student_month_control_summary_{test_result.id}"
            )]
        ]
        buttons.extend(get_back_to_test_kb().inline_keyboard)

        # Получаем данные состояния для очистки сообщений
        data = await state.get_data()

        # Очищаем сообщения теста
        await cleanup_test_messages(chat_id, data, bot)

        await bot.send_message(
            chat_id,
            result_text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
        )
        await state.set_state(StudentTestsStates.month_control_result)

        logger.info(f"Показана статистика контрольного теста месяца для студента {test_result.student_id}")

    except Exception as e:
        logger.error(f"Ошибка при показе статистики контрольного теста месяца: {e}")
        await bot.send_message(
            chat_id,
            "❌ Ошибка при получении статистики",
            reply_markup=get_back_to_test_kb()
        )


# Обработчики кнопок "Начать тест" для тестов месяца
@router.callback_query(StudentTestsStates.month_entry_confirmation, F.data == "start_month_entry_test")
async def start_month_entry_test_confirmed(callback: CallbackQuery, state: FSMContext):
    """Запуск входного теста месяца после подтверждения"""
    try:
        data = await state.get_data()
        questions = data.get("questions")
        month_test_id = data.get("month_test_id")
        student_id = data.get("student_id")

        if not all([questions, month_test_id, student_id]):
            logger.error("Отсутствуют данные для запуска входного теста месяца")
            await callback.answer("❌ Ошибка: данные теста не найдены", show_alert=True)
            return

        # Сохраняем данные для quiz_registrator
        await state.update_data(
            month_test_id=month_test_id,
            student_id=student_id,
            questions=questions,
            q_index=0,
            score=0,
            question_results=[]
        )

        # ВАЖНО: Устанавливаем состояние ПЕРЕД запуском теста
        await state.set_state(StudentTestsStates.test_in_progress)

        # Запускаем тест через quiz_registrator
        await send_next_question(
            chat_id=callback.message.chat.id,
            state=state,
            bot=callback.bot,
            finish_callback=finish_month_entry_test
        )

        logger.info(f"Запущен входной тест месяца: {len(questions)} вопросов")

    except Exception as e:
        logger.error(f"Ошибка при запуске входного теста месяца: {e}")
        await callback.message.edit_text(
            "❌ Произошла ошибка при запуске теста. Попробуйте позже.",
            reply_markup=get_back_to_test_kb()
        )


@router.callback_query(StudentTestsStates.month_control_confirmation, F.data == "start_month_control_test")
async def start_month_control_test_confirmed(callback: CallbackQuery, state: FSMContext):
    """Запуск контрольного теста месяца после подтверждения"""
    try:
        data = await state.get_data()
        questions = data.get("questions")
        month_test_id = data.get("month_test_id")
        student_id = data.get("student_id")

        if not all([questions, month_test_id, student_id]):
            logger.error("Отсутствуют данные для запуска контрольного теста месяца")
            await callback.answer("❌ Ошибка: данные теста не найдены", show_alert=True)
            return

        # Сохраняем данные для quiz_registrator
        await state.update_data(
            month_test_id=month_test_id,
            student_id=student_id,
            questions=questions,
            q_index=0,
            score=0,
            question_results=[]
        )

        # ВАЖНО: Устанавливаем состояние ПЕРЕД запуском теста
        await state.set_state(StudentTestsStates.test_in_progress)

        # Запускаем тест через quiz_registrator
        await send_next_question(
            chat_id=callback.message.chat.id,
            state=state,
            bot=callback.bot,
            finish_callback=finish_month_control_test
        )

        logger.info(f"Запущен контрольный тест месяца: {len(questions)} вопросов")

    except Exception as e:
        logger.error(f"Ошибка при запуске контрольного теста месяца: {e}")
        await callback.message.edit_text(
            "❌ Произошла ошибка при запуске теста. Попробуйте позже.",
            reply_markup=get_back_to_test_kb()
        )


# Функции для использования в transitions.py
async def handle_month_entry_confirmation(callback, state=None, user_role: str = None):
    """Обработчик состояния подтверждения входного теста месяца для навигации"""
    from .base_handlers import show_month_entry_subjects
    await show_month_entry_subjects(callback, state)


async def handle_month_control_confirmation(callback, state=None, user_role: str = None):
    """Обработчик состояния подтверждения контрольного теста месяца для навигации"""
    from .base_handlers import show_month_control_subjects
    await show_month_control_subjects(callback, state)
