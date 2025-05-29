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

router = Router()

# Обработчики для входного теста курса
@router.callback_query(F.data == "course_entry_test")
async def show_course_entry_subjects(callback: CallbackQuery, state: FSMContext):
    """Показать предметы для входного теста курса"""
    current_state = await state.get_state()
    logger.info(f"ВЫЗОВ: show_course_entry_subjects, user_id={callback.from_user.id}, текущее состояние={current_state}")
    await callback.message.edit_text(
        "Выберите предмет для входного теста курса:",
        reply_markup=get_test_subjects_kb("course_entry")
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
        reply_markup=get_test_subjects_kb("month_entry")
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
        "Выберите месяц для входного теста:",
        reply_markup=get_month_test_kb("month_entry", subject_id)
    )
    await state.set_state(StudentTestsStates.select_month_entry)
    logger.info(f"УСТАНОВЛЕНО СОСТОЯНИЕ: StudentTestsStates.select_month_entry")

@router.callback_query(StudentTestsStates.select_month_entry, F.data.startswith("month_entry_"))
async def handle_month_entry_month(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора месяца для входного теста"""
    current_state = await state.get_state()
    logger.info(f"ВЫЗОВ: handle_month_entry_month, user_id={callback.from_user.id}, data={callback.data}, текущее состояние={current_state}")
    # Извлекаем ID предмета и месяц из callback_data
    # Формат: month_entry_SUBJECT_month_NUMBER
    parts = callback.data.split("_")
    subject_id = parts[2]
    month = parts[4]
    
    await handle_entry_test(callback, state, "month_entry", subject_id, month)

# Обработчики для контрольного теста месяца
@router.callback_query(F.data == "month_control_test")
async def show_month_control_subjects(callback: CallbackQuery, state: FSMContext):
    """Показать предметы для контрольного теста месяца"""
    current_state = await state.get_state()
    logger.info(f"ВЫЗОВ: show_month_control_subjects, user_id={callback.from_user.id}, текущее состояние={current_state}")
    await callback.message.edit_text(
        "Выберите предмет для контрольного теста месяца:",
        reply_markup=get_test_subjects_kb("month_control")
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
    
    # Добавляем информацию о каждой теме
    for topic, percentage in topics_percentages.items():
        status = "✅" if percentage >= 80 else "❌" if percentage <= 40 else "⚠️"
        result_text += f"• {topic} — {percentage}% {status}\n"
    
    # Определяем сильные и слабые темы
    strong_topics = [topic for topic, percentage in topics_percentages.items() 
                    if percentage >= 80]
    weak_topics = [topic for topic, percentage in topics_percentages.items() 
                  if percentage <= 40]
    
    # Добавляем информацию о сильных и слабых темах
    if strong_topics:
        result_text += "\n🟢 Сильные темы (≥80%):\n"
        for topic in strong_topics:
            result_text += f"• {topic}\n"
    
    if weak_topics:
        result_text += "\n🔴 Слабые темы (≤40%):\n"
        for topic in weak_topics:
            result_text += f"• {topic}\n"
    
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

def generate_random_questions(count: int):
    """Генерация случайных вопросов для теста"""
    # В реальном приложении здесь будет запрос к базе данных
    # Для примера используем фиксированные значения
    questions = []
    topics = ["Алканы", "Изомерия", "Кислоты"]
    
    for i in range(count):
        topic = topics[i % len(topics)]
        question = {
            "id": i + 1,
            "text": f"Вопрос {i + 1} по теме {topic}",
            "topic": topic,
            "options": {
                "A": f"Вариант A для вопроса {i + 1}",
                "B": f"Вариант B для вопроса {i + 1}",
                "C": f"Вариант C для вопроса {i + 1}",
                "D": f"Вариант D для вопроса {i + 1}"
            },
            "correct": "A"  # Для примера все правильные ответы - A
        }
        questions.append(question)
    
    return questions

# Базовые обработчики для разных типов тестов
async def handle_entry_test(callback: CallbackQuery, state: FSMContext, test_type: str, subject_id: str, month: str = None):
    """Обработчик для входных тестов (курса или месяца)"""
    logger.info(f"ВЫЗОВ: handle_entry_test, user_id={callback.from_user.id}, тип={test_type}, предмет={subject_id}, месяц={month}")
    # Формируем ID теста в зависимости от типа
    if test_type == "course_entry":
        test_id = f"course_entry_{subject_id}"
    else:  # month_entry
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
        question_count = 30 if test_type == "course_entry" else 20
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