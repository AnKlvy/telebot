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

        # Получаем микротемы теста
        microtopics = await month_test.get_microtopics()
        if not microtopics:
            logger.error(f"У теста месяца {month_test_id} нет микротем")
            return []

        all_questions = []
        
        # Для каждой микротемы берем 3 случайных вопроса из домашних заданий
        for microtopic in microtopics:
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

        # Получаем статистику по микротемам
        microtopic_stats = await MonthEntryTestResultRepository.get_microtopic_statistics(test_result.id)

        # Получаем названия микротем
        month_test = await MonthTestRepository.get_by_id(month_test_id)
        microtopics = await MicrotopicRepository.get_by_subject(month_test.subject_id)
        microtopic_names = {mt.number: mt.name for mt in microtopics}

        # Формируем текст результата
        result_text = f"📊 Входной тест месяца завершен!\n\n"
        result_text += f"📗 {month_test.subject.name}:\n"
        result_text += f"Тест: {month_test.name}\n"
        result_text += f"Верных: {test_result.correct_answers} / {test_result.total_questions}\n"
        result_text += f"Процент: {test_result.score_percentage}%\n\n"

        # Добавляем статистику по микротемам
        if microtopic_stats:
            result_text += "📈 Результаты по микротемам:\n"
            for microtopic_num, stats in microtopic_stats.items():
                microtopic_name = microtopic_names.get(microtopic_num, f"Микротема {microtopic_num}")
                percentage = stats['percentage']
                status = "✅" if percentage >= 80 else "❌" if percentage <= 40 else "⚠️"
                result_text += f"• {microtopic_name} — {percentage}% {status}\n"

        # Очищаем сообщения теста
        await cleanup_test_messages(chat_id, data, bot)

        await bot.send_message(
            chat_id,
            result_text,
            reply_markup=get_back_to_test_kb()
        )
        await state.set_state(StudentTestsStates.test_result)

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
        # Получаем статистику по микротемам
        microtopic_stats = await MonthControlTestResultRepository.get_microtopic_statistics(test_result.id)

        # Получаем названия микротем
        microtopics = await MicrotopicRepository.get_by_subject(test_result.month_test.subject_id)
        microtopic_names = {mt.number: mt.name for mt in microtopics}

        # Пытаемся найти соответствующий входной тест для сравнения
        entry_test = None
        comparison_text = ""
        if test_result.month_test.parent_test_id:
            entry_test = await MonthTestRepository.get_by_id(test_result.month_test.parent_test_id)
            if entry_test:
                entry_result = await MonthEntryTestResultRepository.get_by_student_and_month_test(
                    test_result.student_id, entry_test.id
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
        result_text += f"📗 {test_result.month_test.subject.name}\n"
        result_text += f"Тест: {test_result.month_test.name}\n"
        result_text += f"Верных ответов: {test_result.correct_answers} / {test_result.total_questions}\n"
        result_text += f"Процент: {test_result.score_percentage}%\n"
        result_text += comparison_text

        # Добавляем статистику по микротемам
        if microtopic_stats:
            result_text += "\n📈 Результаты по микротемам:\n"
            for microtopic_num, stats in microtopic_stats.items():
                microtopic_name = microtopic_names.get(microtopic_num, f"Микротема {microtopic_num}")
                percentage = stats['percentage']
                status = "✅" if percentage >= 80 else "❌" if percentage <= 40 else "⚠️"
                result_text += f"• {microtopic_name} — {percentage}% {status}\n"

        # Очищаем сообщения теста
        await cleanup_test_messages(chat_id, data, bot)

        await bot.send_message(
            chat_id,
            result_text,
            reply_markup=get_back_to_test_kb()
        )
        await state.set_state(StudentTestsStates.test_result)

        logger.info(f"Показана статистика контрольного теста месяца для студента {test_result.student_id}")

    except Exception as e:
        logger.error(f"Ошибка при показе статистики контрольного теста месяца: {e}")
        await bot.send_message(
            chat_id,
            "❌ Ошибка при получении статистики",
            reply_markup=get_back_to_test_kb()
        )
