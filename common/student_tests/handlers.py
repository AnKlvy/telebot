import logging

# Настройка логгера
logger = logging.getLogger(__name__)

from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from .states import StudentTestsStates
from .keyboards import (
    get_test_subjects_kb,
    get_month_test_kb,
    get_back_to_test_kb,
    get_test_answers_kb
)
from common.statistics import (
    get_test_results,
    format_test_result,
    format_test_comparison
)
from database.repositories.month_test_repository import MonthTestRepository
from database.repositories.month_entry_test_result_repository import MonthEntryTestResultRepository
from database.repositories.question_repository import QuestionRepository
from database.repositories.microtopic_repository import MicrotopicRepository
from database.repositories.student_repository import StudentRepository
from database.repositories.user_repository import UserRepository
from database.repositories.subject_repository import SubjectRepository
import random

router = Router()

# Обработчики для входного теста курса
@router.callback_query(F.data == "course_entry_test")
async def show_course_entry_subjects(callback: CallbackQuery, state: FSMContext):
    """Показать предметы для входного теста курса"""
    current_state = await state.get_state()
    logger.info(f"ВЫЗОВ: show_course_entry_subjects, user_id={callback.from_user.id}, текущее состояние={current_state}")
    await callback.message.edit_text(
        "Выберите предмет для входного теста курса:",
        reply_markup=await get_test_subjects_kb("course_entry", user_id=callback.from_user.id)
    )
    await state.set_state(StudentTestsStates.select_group_entry)
    logger.info(f"УСТАНОВЛЕНО СОСТОЯНИЕ: StudentTestsStates.select_group_entry")

@router.callback_query(StudentTestsStates.select_group_entry, F.data.startswith("course_entry_sub_"))
async def handle_course_entry_subject(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора предмета для входного теста курса"""
    current_state = await state.get_state()
    logger.info(f"ВЫЗОВ: handle_course_entry_subject, user_id={callback.from_user.id}, data={callback.data}, текущее состояние={current_state}")
    subject_id = callback.data.replace("course_entry_sub_", "")
    await handle_entry_test(callback, state, "course_entry", subject_id)

# Обработчики для входного теста месяца
@router.callback_query(F.data == "month_entry_test")
async def show_month_entry_subjects(callback: CallbackQuery, state: FSMContext):
    """Показать предметы для входного теста месяца"""
    current_state = await state.get_state()
    logger.info(f"ВЫЗОВ: show_month_entry_subjects, user_id={callback.from_user.id}, текущее состояние={current_state}")
    await callback.message.edit_text(
        "Выберите предмет для входного теста месяца:",
        reply_markup=await get_test_subjects_kb("month_entry", user_id=callback.from_user.id)
    )
    await state.set_state(StudentTestsStates.select_group_entry)
    logger.info(f"УСТАНОВЛЕНО СОСТОЯНИЕ: StudentTestsStates.select_group_entry")

@router.callback_query(StudentTestsStates.select_group_entry, F.data.startswith("month_entry_sub_"))
async def handle_month_entry_subject(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора предмета для входного теста месяца"""
    current_state = await state.get_state()
    logger.info(f"ВЫЗОВ: handle_month_entry_subject, user_id={callback.from_user.id}, data={callback.data}, текущее состояние={current_state}")
    subject_id = callback.data.replace("month_entry_sub_", "")
    await callback.message.edit_text(
        "Выберите тест месяца:",
        reply_markup=await get_month_test_kb("month_entry", subject_id, callback.from_user.id)
    )
    await state.set_state(StudentTestsStates.select_month_entry)
    logger.info(f"УСТАНОВЛЕНО СОСТОЯНИЕ: StudentTestsStates.select_month_entry")

@router.callback_query(StudentTestsStates.select_month_entry, F.data.startswith("month_entry_"))
async def handle_month_entry_month(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора теста месяца для входного теста"""
    current_state = await state.get_state()
    logger.info(f"ВЫЗОВ: handle_month_entry_month, user_id={callback.from_user.id}, data={callback.data}, текущее состояние={current_state}")

    # Извлекаем ID предмета и ID теста из callback_data
    # Формат: month_entry_SUBJECT_test_TEST_ID
    parts = callback.data.split("_")
    if len(parts) >= 4 and parts[3] == "test":
        subject_id = parts[2]
        test_id = int(parts[4])
        await handle_month_entry_test_by_id(callback, state, subject_id, test_id)
    else:
        # Старый формат для обратной совместимости
        subject_id = parts[2]
        month = parts[4] if len(parts) > 4 else "1"
        await handle_entry_test(callback, state, "month_entry", subject_id, month)

# Обработчики для контрольного теста месяца
@router.callback_query(F.data == "month_control_test")
async def show_month_control_subjects(callback: CallbackQuery, state: FSMContext):
    """Показать предметы для контрольного теста месяца"""
    current_state = await state.get_state()
    logger.info(f"ВЫЗОВ: show_month_control_subjects, user_id={callback.from_user.id}, текущее состояние={current_state}")
    await callback.message.edit_text(
        "Выберите предмет для контрольного теста месяца:",
        reply_markup=await get_test_subjects_kb("month_control", user_id=callback.from_user.id)
    )
    await state.set_state(StudentTestsStates.select_group_control)
    logger.info(f"УСТАНОВЛЕНО СОСТОЯНИЕ: StudentTestsStates.select_group_control")

@router.callback_query(StudentTestsStates.select_group_control, F.data.startswith("month_control_sub_"))
async def handle_month_control_subject(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора предмета для контрольного теста месяца"""
    current_state = await state.get_state()
    logger.info(f"ВЫЗОВ: handle_month_control_subject, user_id={callback.from_user.id}, data={callback.data}, текущее состояние={current_state}")
    subject_id = callback.data.replace("month_control_sub_", "")
    await callback.message.edit_text(
        "Выберите месяц для контрольного теста:",
        reply_markup=get_month_test_kb("month_control", subject_id)
    )
    await state.set_state(StudentTestsStates.select_month_control)
    logger.info(f"УСТАНОВЛЕНО СОСТОЯНИЕ: StudentTestsStates.select_month_control")

@router.callback_query(StudentTestsStates.select_month_control, F.data.startswith("month_control_"))
async def handle_month_control_month(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора месяца для контрольного теста"""
    current_state = await state.get_state()
    logger.info(f"ВЫЗОВ: handle_month_control_month, user_id={callback.from_user.id}, data={callback.data}, текущее состояние={current_state}")
    # Извлекаем ID предмета и месяц из callback_data
    # Формат: month_control_SUBJECT_month_NUMBER
    parts = callback.data.split("_")
    subject_id = parts[2]
    month = parts[4]
    
    await handle_control_test(callback, state, subject_id, month)

# Обработчики для прохождения теста
@router.callback_query(StudentTestsStates.test_in_progress, F.data.startswith("answer_"))
async def handle_test_answer(callback: CallbackQuery, state: FSMContext):
    """Обработка ответа на вопрос теста"""
    current_state = await state.get_state()
    logger.info(f"ВЫЗОВ: handle_test_answer, user_id={callback.from_user.id}, data={callback.data}, текущее состояние={current_state}")
    await process_test_answer(callback, state)

# Обработчики для детальной аналитики перенесены в student/handlers/test_report.py

# Обработчики для возврата в меню тестов
@router.callback_query(F.data == "back_to_tests")
async def back_to_tests(callback: CallbackQuery, state: FSMContext):
    """Возврат в меню тестов"""
    current_state = await state.get_state()
    logger.info(f"ВЫЗОВ: back_to_tests, user_id={callback.from_user.id}, текущее состояние={current_state}")
    from .menu import show_tests_menu
    await show_tests_menu(callback, state)
    logger.info(f"УСТАНОВЛЕНО СОСТОЯНИЕ: StudentTestsStates.main")

async def show_test_question(callback: CallbackQuery, state: FSMContext, question_number: int):
    """Показать вопрос теста"""
    current_state = await state.get_state()
    logger.info(f"ВЫЗОВ: show_test_question, user_id={callback.from_user.id}, question={question_number}, текущее состояние={current_state}")
    user_data = await state.get_data()
    test_questions = user_data.get("test_questions", [])
    
    if question_number > len(test_questions):
        # Если вопросы закончились, завершаем тест
        logger.info(f"ЗАВЕРШЕНИЕ ТЕСТА: вопросы закончились")
        await finish_test(callback, state)
        return
    
    question = test_questions[question_number - 1]
    options_text = "\n".join([f"{key}) {value}" for key, value in question["options"].items()])
    
    await callback.message.edit_text(
        f"Вопрос {question_number}/{len(test_questions)}\n\n"
        f"{question['text']}\n\n"
        f"{options_text}",
        reply_markup=get_test_answers_kb()
    )
    logger.info(f"ПОКАЗАН ВОПРОС: {question_number}/{len(test_questions)}")

async def process_test_answer(callback: CallbackQuery, state: FSMContext):
    """Обработка ответа на вопрос теста"""
    current_state = await state.get_state()
    logger.info(f"ВЫЗОВ: process_test_answer, user_id={callback.from_user.id}, текущее состояние={current_state}")
    selected_answer = callback.data.replace("answer_", "")
    user_data = await state.get_data()
    current_question = user_data.get("current_question", 1)
    test_questions = user_data.get("test_questions", [])
    
    logger.info(f"ОТВЕТ: {selected_answer} на вопрос {current_question}")
    
    if current_question <= len(test_questions):
        question = test_questions[current_question - 1]
        
        # Проверяем правильность ответа
        is_correct = selected_answer == question["correct"]
        logger.info(f"ПРАВИЛЬНОСТЬ: {'верно' if is_correct else 'неверно'}")
        
        # Обновляем статистику по темам
        topics_progress = user_data.get("topics_progress", {})
        topic = question.get("topic", "Неизвестная тема")
        
        if topic not in topics_progress:
            topics_progress[topic] = {"correct": 0, "total": 0}
        
        topics_progress[topic]["total"] += 1
        if is_correct:
            topics_progress[topic]["correct"] += 1
        
        # Сохраняем ответ пользователя
        user_answers = user_data.get("user_answers", {})
        user_answers[current_question] = {
            "selected": selected_answer,
            "correct": is_correct,
            "topic": topic
        }
        
        # Обновляем счетчик правильных ответов
        correct_answers = user_data.get("correct_answers", 0)
        if is_correct:
            correct_answers += 1
        
        # Обновляем данные состояния
        next_question = current_question + 1
        await state.update_data(
            current_question=next_question,
            correct_answers=correct_answers,
            user_answers=user_answers,
            topics_progress=topics_progress
        )
        logger.info(f"ОБНОВЛЕНО СОСТОЯНИЕ: следующий вопрос {next_question}, правильных ответов {correct_answers}")
        
        # Если есть следующий вопрос, показываем его
        if next_question <= len(test_questions):
            logger.info(f"ПЕРЕХОД: к следующему вопросу {next_question}")
            await show_test_question(callback, state, next_question)
        else:
            # Иначе завершаем тест
            logger.info(f"ЗАВЕРШЕНИЕ ТЕСТА: все вопросы отвечены")
            await finish_test(callback, state)
    else:
        # Если все вопросы пройдены, завершаем тест
        logger.info(f"ЗАВЕРШЕНИЕ ТЕСТА: все вопросы уже отвечены")
        await finish_test(callback, state)

async def finish_test(callback: CallbackQuery, state: FSMContext):
    """Завершение теста и показ результатов"""
    current_state = await state.get_state()
    logger.info(f"ВЫЗОВ: finish_test, user_id={callback.from_user.id}, текущее состояние={current_state}")
    user_data = await state.get_data()
    test_type = user_data.get("test_type", "")
    selected_subject = user_data.get("selected_subject", "")
    selected_month = user_data.get("selected_month", "")
    total_questions = user_data.get("total_questions", 0)
    correct_answers = user_data.get("correct_answers", 0)
    topics_progress = user_data.get("topics_progress", {})
    
    logger.info(f"РЕЗУЛЬТАТЫ: тип={test_type}, предмет={selected_subject}, месяц={selected_month}, верных={correct_answers}/{total_questions}")
    
    # Определяем название предмета
    subject_names = {
        "kz": "История Казахстана",
        "mathlit": "Математическая грамотность",
        "math": "Математика",
        "geo": "География",
        "bio": "Биология",
        "chem": "Химия",
        "inf": "Информатика",
        "world": "Всемирная история"
    }
    subject_name = subject_names.get(selected_subject, "Неизвестный предмет")
    
    # Вычисляем процент понимания по каждой теме
    topics_percentages = {}
    for topic, data in topics_progress.items():
        if data["total"] > 0:
            percentage = int((data["correct"] / data["total"]) * 100)
            topics_percentages[topic] = percentage
            logger.info(f"ТЕМА: {topic}, процент={percentage}%")
    
    # Формируем текст с результатами в зависимости от типа теста
    if test_type == "course_entry":
        result_text = f"📊 Входной тест курса пройден\nРезультат:\n📗 {subject_name}:\n"
    elif test_type == "month_entry":
        result_text = f"📊 Входной тест месяца {selected_month} пройден\nРезультат:\n📗 {subject_name}:\n"
    elif test_type == "month_control":
        result_text = f"📊 Контрольный тест месяца {selected_month} пройден\nРезультат:\n📗 {subject_name}:\n"
    else:
        result_text = f"📊 Тест пройден\nРезультат:\n📗 {subject_name}:\n"
    
    result_text += f"Верных: {correct_answers} / {total_questions}\n"
    
    # Добавляем информацию о каждой теме с единым форматированием
    for topic, percentage in topics_percentages.items():
        status = "✅" if percentage >= 80 else "❌" if percentage <= 40 else "⚠️"
        result_text += f"• {topic} — {percentage}% {status}\n"

    # Используем единую функцию для добавления сильных и слабых тем
    from common.statistics import add_strong_and_weak_topics
    result_text = add_strong_and_weak_topics(result_text, topics_percentages)
    
    # Сохраняем результаты теста
    test_results = {
        "total_questions": total_questions,
        "correct_answers": correct_answers,
        "topics_progress": topics_percentages
    }
    
    # В реальном приложении здесь будет сохранение результатов в базу данных
    # Для примера просто сохраняем в состоянии
    await state.update_data(
        test_completed=True,
        test_results=test_results
    )
    logger.info(f"СОХРАНЕНЫ РЕЗУЛЬТАТЫ: {test_results}")
    
    await callback.message.edit_text(
        result_text,
        reply_markup=get_back_to_test_kb()
    )
    await state.set_state(StudentTestsStates.test_result)
    logger.info(f"УСТАНОВЛЕНО СОСТОЯНИЕ: StudentTestsStates.test_result")

async def generate_month_test_questions(month_test_id: int) -> list:
    """Генерация вопросов для входного теста месяца из ДЗ по микротемам"""
    try:
        # Получаем тест месяца с микротемами
        month_test = await MonthTestRepository.get_by_id(month_test_id)
        if not month_test:
            logger.error(f"Тест месяца с ID {month_test_id} не найден")
            return []

        # Получаем все вопросы по предмету
        all_questions = await QuestionRepository.get_by_subject(month_test.subject_id)
        if not all_questions:
            logger.warning(f"Нет вопросов для предмета {month_test.subject_id}")
            return []

        # Группируем вопросы по микротемам
        questions_by_microtopic = {}
        for question in all_questions:
            if question.microtopic_number:
                if question.microtopic_number not in questions_by_microtopic:
                    questions_by_microtopic[question.microtopic_number] = []
                questions_by_microtopic[question.microtopic_number].append(question)

        # Формируем список вопросов для теста
        test_questions = []

        # Для каждой микротемы в тесте выбираем до 3 случайных вопросов
        for microtopic_link in month_test.microtopics:
            microtopic_number = microtopic_link.microtopic_number
            available_questions = questions_by_microtopic.get(microtopic_number, [])

            if available_questions:
                # Выбираем до 3 случайных вопросов
                selected_count = min(3, len(available_questions))
                selected_questions = random.sample(available_questions, selected_count)

                # Добавляем вопросы в формате для quiz_registrator
                for question in selected_questions:
                    test_questions.append({
                        'id': question.id,
                        'text': question.text,
                        'photo_path': question.photo_path,
                        'time_limit': question.time_limit,
                        'microtopic_number': question.microtopic_number
                    })

                logger.info(f"Добавлено {selected_count} вопросов для микротемы {microtopic_number}")
            else:
                logger.warning(f"Нет вопросов для микротемы {microtopic_number}")

        logger.info(f"Сгенерировано {len(test_questions)} вопросов для теста месяца")
        return test_questions

    except Exception as e:
        logger.error(f"Ошибка при генерации вопросов для теста месяца: {e}")
        return []


async def finish_month_entry_test(callback: CallbackQuery, state: FSMContext):
    """Завершение входного теста месяца и сохранение результатов в БД"""
    try:
        data = await state.get_data()
        question_results = data.get("question_results", [])
        month_test_id = data.get("month_test_id")
        student_id = data.get("student_id")

        if not month_test_id or not student_id:
            logger.error("Нет данных о тесте или студенте")
            await callback.message.edit_text(
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

        await callback.message.edit_text(
            result_text,
            reply_markup=get_back_to_test_kb()
        )
        await state.set_state(StudentTestsStates.test_result)

        logger.info(f"Тест месяца завершен: студент {student_id}, результат {test_result.score_percentage}%")

    except Exception as e:
        logger.error(f"Ошибка при завершении теста месяца: {e}")
        await callback.message.edit_text(
            "❌ Ошибка при сохранении результатов теста",
            reply_markup=get_back_to_test_kb()
        )


async def handle_month_entry_test_real(callback: CallbackQuery, state: FSMContext, subject_id: str, month_name: str):
    """Обработчик для входного теста месяца с реальной БД"""
    telegram_id = callback.from_user.id
    logger.info(f"ВЫЗОВ: handle_month_entry_test_real, telegram_id={telegram_id}, subject_id={subject_id}, month={month_name}")

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

        # Преобразуем subject_id в реальный ID предмета
        subject_mapping = {
            "kz": "История Казахстана",
            "mathlit": "Математическая грамотность",
            "math": "Математика",
            "geo": "География",
            "bio": "Биология",
            "chem": "Химия",
            "inf": "Информатика",
            "world": "Всемирная история",
            "python": "Python",
            "js": "JavaScript",
            "java": "Java",
            "physics": "Физика"
        }

        subject_name = subject_mapping.get(subject_id, subject_id)
        subject = await SubjectRepository.get_by_name(subject_name)
        if not subject:
            await callback.message.edit_text(
                f"❌ Предмет '{subject_name}' не найден",
                reply_markup=get_back_to_test_kb()
            )
            return

        # Получаем курсы студента
        from database.repositories.course_repository import CourseRepository
        student_courses = await CourseRepository.get_by_student(student.id)
        if not student_courses:
            await callback.message.edit_text(
                "❌ У студента нет назначенных курсов",
                reply_markup=get_back_to_test_kb()
            )
            return

        # Ищем тест месяца для данного предмета и месяца в курсах студента
        month_test = None
        for course in student_courses:
            test = await MonthTestRepository.get_by_course_subject_month(
                course_id=course.id,
                subject_id=subject.id,
                month_name=month_name
            )
            if test and test.test_type == 'entry':
                month_test = test
                break

        if not month_test:
            await callback.message.edit_text(
                f"❌ Входной тест месяца '{month_name}' для предмета '{subject_name}' не найден",
                reply_markup=get_back_to_test_kb()
            )
            return

        # Проверяем, не проходил ли студент уже этот тест
        existing_result = await MonthEntryTestResultRepository.get_by_student_and_month_test(
            student_id=student.id,
            month_test_id=month_test.id
        )

        if existing_result:
            # Тест уже пройден - показываем статистику
            await show_month_entry_test_statistics(callback, state, existing_result)
            return

        # Генерируем вопросы для теста
        test_questions = await generate_month_test_questions(month_test.id)
        if not test_questions:
            await callback.message.edit_text(
                "❌ Не удалось сгенерировать вопросы для теста",
                reply_markup=get_back_to_test_kb()
            )
            return

        # Сохраняем данные для quiz_registrator
        await state.update_data(
            month_test_id=month_test.id,
            student_id=student.id,
            questions=test_questions,
            q_index=0,
            score=0,
            question_results=[]
        )

        # Запускаем тест через quiz_registrator
        await send_question(
            chat_id=callback.message.chat.id,
            state=state,
            bot=callback.bot,
            finish_callback=finish_month_entry_test
        )

        logger.info(f"Запущен входной тест месяца: {len(test_questions)} вопросов")

    except Exception as e:
        logger.error(f"Ошибка при обработке входного теста месяца: {e}")
        await callback.message.edit_text(
            "❌ Произошла ошибка при запуске теста",
            reply_markup=get_back_to_test_kb()
        )


async def show_month_entry_test_statistics(callback: CallbackQuery, state: FSMContext, test_result):
    """Показать статистику уже пройденного входного теста месяца"""
    try:
        # Получаем статистику по микротемам
        microtopic_stats = await MonthEntryTestResultRepository.get_microtopic_statistics(test_result.id)

        # Получаем названия микротем
        microtopics = await MicrotopicRepository.get_by_subject(test_result.month_test.subject_id)
        microtopic_names = {mt.number: mt.name for mt in microtopics}

        # Формируем текст результата (такой же как у куратора)
        result_text = f"📊 Результат входного теста месяца\n\n"
        result_text += f"📗 {test_result.month_test.subject.name}:\n"
        result_text += f"Тест: {test_result.month_test.name}\n"
        result_text += f"Верных: {test_result.correct_answers} / {test_result.total_questions}\n"
        result_text += f"Процент: {test_result.score_percentage}%\n"
        result_text += f"Дата прохождения: {test_result.completed_at.strftime('%d.%m.%Y %H:%M')}\n\n"

        # Добавляем статистику по микротемам
        if microtopic_stats:
            result_text += "📈 Результаты по микротемам:\n"
            for microtopic_num, stats in microtopic_stats.items():
                microtopic_name = microtopic_names.get(microtopic_num, f"Микротема {microtopic_num}")
                percentage = stats['percentage']
                status = "✅" if percentage >= 80 else "❌" if percentage <= 40 else "⚠️"
                result_text += f"• {microtopic_name} — {percentage}% {status}\n"

        await callback.message.edit_text(
            result_text,
            reply_markup=get_back_to_test_kb()
        )
        await state.set_state(StudentTestsStates.test_result)

        logger.info(f"Показана статистика теста месяца для студента {test_result.student_id}")

    except Exception as e:
        logger.error(f"Ошибка при показе статистики теста месяца: {e}")
        await callback.message.edit_text(
            "❌ Ошибка при загрузке статистики теста",
            reply_markup=get_back_to_test_kb()
        )


async def handle_month_entry_test_by_id(callback: CallbackQuery, state: FSMContext, subject_id: str, test_id: int):
    """Обработчик для входного теста месяца по ID теста"""
    telegram_id = callback.from_user.id
    logger.info(f"ВЫЗОВ: handle_month_entry_test_by_id, telegram_id={telegram_id}, subject_id={subject_id}, test_id={test_id}")

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

        # Получаем тест месяца по ID
        month_test = await MonthTestRepository.get_by_id(test_id)
        if not month_test or month_test.test_type != 'entry':
            await callback.message.edit_text(
                "❌ Входной тест месяца не найден",
                reply_markup=get_back_to_test_kb()
            )
            return

        # Проверяем, не проходил ли студент уже этот тест
        existing_result = await MonthEntryTestResultRepository.get_by_student_and_month_test(
            student_id=student.id,
            month_test_id=month_test.id
        )

        if existing_result:
            # Тест уже пройден - показываем статистику
            await show_month_entry_test_statistics(callback, state, existing_result)
            return

        # Генерируем вопросы для теста
        test_questions = await generate_month_test_questions(month_test.id)
        if not test_questions:
            await callback.message.edit_text(
                "❌ Не удалось сгенерировать вопросы для теста",
                reply_markup=get_back_to_test_kb()
            )
            return

        # Сохраняем данные для quiz_registrator
        await state.update_data(
            month_test_id=month_test.id,
            student_id=student.id,
            questions=test_questions,
            q_index=0,
            score=0,
            question_results=[]
        )

        # Запускаем тест через quiz_registrator
        await send_question(
            chat_id=callback.message.chat.id,
            state=state,
            bot=callback.bot,
            finish_callback=finish_month_entry_test
        )

        logger.info(f"Запущен входной тест месяца: {len(test_questions)} вопросов")

    except Exception as e:
        logger.error(f"Ошибка при обработке входного теста месяца по ID: {e}")
        await callback.message.edit_text(
            "❌ Произошла ошибка при запуске теста",
            reply_markup=get_back_to_test_kb()
        )


# Регистрируем обработчики quiz_registrator для входных тестов месяца
from common.quiz_registrator import register_quiz_handlers
register_quiz_handlers(
    router=router,
    test_state=StudentTestsStates.test_in_progress
)

# Базовые обработчики для разных типов тестов
async def handle_entry_test(callback: CallbackQuery, state: FSMContext, test_type: str, subject_id: str, month: str = None):
    """Обработчик для входных тестов (курса или месяца)"""
    logger.info(f"ВЫЗОВ: handle_entry_test, user_id={callback.from_user.id}, тип={test_type}, предмет={subject_id}, месяц={month}")

    if test_type == "course_entry":
        # Для входного теста курса работаем с реальной БД
        await handle_course_entry_test_real(callback, state, subject_id)
    else:
        # Для месячных тестов пока оставляем старую логику
        # Формируем ID теста в зависимости от типа
        test_id = f"month_entry_{subject_id}_{month}"

        # Получаем результаты теста, если они есть
        test_results = get_test_results(test_id, "student1")  # В реальном приложении здесь будет ID студента
        logger.info(f"ПОЛУЧЕНЫ РЕЗУЛЬТАТЫ: {test_results}")

        # Определяем название предмета
        subject_names = {
            "kz": "История Казахстана",
            "mathlit": "Математическая грамотность",
            "math": "Математика",
            "geo": "География",
            "bio": "Биология",
            "chem": "Химия",
            "inf": "Информатика",
            "world": "Всемирная история"
        }
        subject_name = subject_names.get(subject_id, "Неизвестный предмет")

        if test_results and test_results.get("total_questions", 0) > 0:
            # Если тест уже пройден, показываем результаты
            logger.info(f"ТЕСТ УЖЕ ПРОЙДЕН: показываем результаты")
            result_text = format_test_result(test_results, subject_name, test_type, month)

            await callback.message.edit_text(
                result_text,
                reply_markup=get_back_to_test_kb()
            )
            await state.set_state(StudentTestsStates.test_result)
        else:
            # Если тест еще не пройден, начинаем его
            # Сохраняем информацию о выбранном предмете и месяце
            await state.update_data(selected_subject=subject_id, selected_month=month)

            # Получаем случайные вопросы для теста
            question_count = 20
            test_questions = generate_random_questions(question_count)

            await state.update_data(
                test_started=True,
                test_type=test_type,
                total_questions=len(test_questions),
                current_question=1,
                correct_answers=0,
                user_answers={},
                test_questions=test_questions,
                topics_progress={}
            )

            # Показываем первый вопрос
            await show_test_question(callback, state, 1)
            await state.set_state(StudentTestsStates.test_in_progress)

async def handle_control_test(callback: CallbackQuery, state: FSMContext, subject_id: str, month: str):
    """Обработчик для контрольных тестов месяца"""
    # Формируем ID тестов
    control_test_id = f"month_control_{subject_id}_{month}"
    entry_test_id = f"month_entry_{subject_id}_{month}"
    
    # Получаем результаты тестов
    control_results = get_test_results(control_test_id, "student1")
    entry_results = get_test_results(entry_test_id, "student1")
    
    # Определяем название предмета
    subject_names = {
        "kz": "История Казахстана",
        "mathlit": "Математическая грамотность",
        "math": "Математика",
        "geo": "География",
        "bio": "Биология",
        "chem": "Химия",
        "inf": "Информатика",
        "world": "Всемирная история"
    }
    subject_name = subject_names.get(subject_id, "Неизвестный предмет")
    
    if control_results and control_results.get("total_questions", 0) > 0:
        # Если контрольный тест уже пройден, показываем сравнение результатов
        result_text = format_test_comparison(entry_results, control_results, subject_name, month)
        
        await callback.message.edit_text(
            result_text,
            reply_markup=get_back_to_test_kb()
        )
        await state.set_state(StudentTestsStates.test_result)
    else:
        # Если контрольный тест еще не пройден, начинаем его
        # Сохраняем информацию о выбранном предмете и месяце
        await state.update_data(selected_subject=subject_id, selected_month=month)
        
        # Получаем случайные вопросы для теста
        question_count = 20
        test_questions = generate_random_questions(question_count)
        
        await state.update_data(
            test_started=True,
            test_type="month_control",
            total_questions=len(test_questions),
            current_question=1,
            correct_answers=0,
            user_answers={},
            test_questions=test_questions,
            topics_progress={}
        )
        
        # Показываем первый вопрос
        await show_test_question(callback, state, 1)
        await state.set_state(StudentTestsStates.test_in_progress)


async def handle_course_entry_test_real(callback: CallbackQuery, state: FSMContext, subject_id: str):
    """Обработчик для входного теста курса с реальной БД"""
    from database import (
        CourseEntryTestResultRepository, QuestionRepository,
        StudentRepository, SubjectRepository, UserRepository
    )

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

        # Преобразуем subject_id в реальный ID предмета
        subject_mapping = {
            "kz": "История Казахстана",
            "mathlit": "Математическая грамотность",
            "math": "Математика",
            "geo": "География",
            "bio": "Биология",
            "chem": "Химия",
            "inf": "Информатика",
            "world": "Всемирная история",
            "python": "Python",
            "js": "JavaScript",
            "java": "Java",
            "physics": "Физика"
        }

        subject_name = subject_mapping.get(subject_id, subject_id)
        subject = await SubjectRepository.get_by_name(subject_name)
        if not subject:
            await callback.message.edit_text(
                f"❌ Предмет '{subject_name}' не найден",
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
                f"❌ Нет доступных вопросов по предмету '{subject_name}'\n"
                "Возможно, вы не записаны на курсы с этим предметом или в курсах нет домашних заданий.",
                reply_markup=get_back_to_test_kb()
            )
            return

        logger.info(f"НАЙДЕНО ВОПРОСОВ: {len(questions)} для предмета {subject_name}")

        # Начинаем тест через quiz_registrator
        await start_course_entry_test_with_quiz(callback, state, questions, student.id, subject.id, subject_name)

    except Exception as e:
        logger.error(f"ОШИБКА в handle_course_entry_test_real: {e}")
        await callback.message.edit_text(
            "❌ Произошла ошибка при загрузке теста. Попробуйте позже.",
            reply_markup=get_back_to_test_kb()
        )


async def start_course_entry_test_with_quiz(callback: CallbackQuery, state: FSMContext, questions, student_id: int, subject_id: int, subject_name: str):
    """Запуск входного теста курса через quiz_registrator"""
    from common.quiz_registrator import send_next_question

    logger.info(f"ЗАПУСК ТЕСТА: {len(questions)} вопросов для студента {student_id}")

    # Подготавливаем данные вопросов для quiz_registrator
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

    # Запускаем первый вопрос
    await send_next_question(
        chat_id=callback.message.chat.id,
        state=state,
        bot=callback.bot,
        finish_callback=finish_course_entry_test
    )

    await state.set_state(StudentTestsStates.test_in_progress)


async def finish_course_entry_test_handler(chat_id: int, state: FSMContext, bot):
    """Обработчик завершения входного теста курса"""
    from database import CourseEntryTestResultRepository
    from common.quiz_registrator import cleanup_test_messages

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
        await state.set_state(StudentTestsStates.test_result)

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
        await state.set_state(StudentTestsStates.test_result)

    except Exception as e:
        logger.error(f"ОШИБКА при показе результатов: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")

        await bot.send_message(
            chat_id,
            "❌ Ошибка при отображении результатов теста."
        )


async def show_student_course_entry_microtopics_detailed(callback: CallbackQuery, state: FSMContext, test_result_id: int):
    """Показать детальную статистику по микротемам входного теста курса для студента"""
    from database import CourseEntryTestResultRepository
    from common.statistics import format_course_entry_test_detailed_microtopics

    try:
        # Получаем результат теста
        test_result = await CourseEntryTestResultRepository.get_by_id(test_result_id)
        if not test_result:
            await callback.message.edit_text(
                "❌ Результат теста не найден",
                reply_markup=get_back_to_test_kb()
            )
            return

        # Форматируем детальную статистику
        result_text = await format_course_entry_test_detailed_microtopics(test_result)

        await callback.message.edit_text(
            result_text,
            reply_markup=get_back_to_test_kb()
        )

    except Exception as e:
        logger.error(f"Ошибка при получении детальной статистики: {e}")
        await callback.message.edit_text(
            "❌ Ошибка при получении детальной статистики",
            reply_markup=get_back_to_test_kb()
        )


async def show_student_course_entry_microtopics_summary(callback: CallbackQuery, state: FSMContext, test_result_id: int):
    """Показать сводку по сильным/слабым темам входного теста курса для студента"""
    from database import CourseEntryTestResultRepository
    from common.statistics import format_course_entry_test_summary_microtopics

    try:
        # Получаем результат теста
        test_result = await CourseEntryTestResultRepository.get_by_id(test_result_id)
        if not test_result:
            await callback.message.edit_text(
                "❌ Результат теста не найден",
                reply_markup=get_back_to_test_kb()
            )
            return

        # Форматируем сводку
        result_text = await format_course_entry_test_summary_microtopics(test_result)

        await callback.message.edit_text(
            result_text,
            reply_markup=get_back_to_test_kb()
        )

    except Exception as e:
        logger.error(f"Ошибка при получении сводки: {e}")
        await callback.message.edit_text(
            "❌ Ошибка при получении сводки",
            reply_markup=get_back_to_test_kb()
        )