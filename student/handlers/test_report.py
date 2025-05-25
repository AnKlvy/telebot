from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from ..keyboards.test_report import (
    get_test_report_menu_kb, 
    get_test_subjects_kb, 
    get_month_test_kb,
    get_back_to_test_report_kb,
    get_test_answers_kb
)
from common.statistics import get_test_results, format_test_result, format_test_comparison

router = Router()

class TestReportStates(StatesGroup):
    main = State()
    course_entry_subject = State()
    month_entry_subject = State()
    month_entry_month = State()
    month_control_subject = State()
    month_control_month = State()
    test_result = State()
    test_in_progress = State()

@router.callback_query(F.data == "test_report")
async def show_test_report_menu(callback: CallbackQuery, state: FSMContext):
    """Показать меню тест-отчета"""
    await callback.message.edit_text(
        "В этом разделе ты можешь пройти входные и контрольные тесты и посмотреть, как растёт твой уровень знаний.\n"
        "Выбери тип теста:",
        reply_markup=get_test_report_menu_kb()
    )
    await state.set_state(TestReportStates.main)

@router.callback_query(TestReportStates.main, F.data == "course_entry_test")
async def choose_course_entry_subject(callback: CallbackQuery, state: FSMContext):
    """Выбор предмета для входного теста курса"""
    await callback.message.edit_text(
        "Выберите предмет для теста:",
        reply_markup=get_test_subjects_kb("course_entry")
    )
    await state.set_state(TestReportStates.course_entry_subject)

@router.callback_query(TestReportStates.course_entry_subject, F.data.startswith("course_entry_sub_"))
async def handle_course_entry_subject(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора предмета для входного теста курса"""
    subject_id = callback.data.replace("course_entry_sub_", "")
    print(f"DEBUG: Обработка выбора предмета для входного теста курса: {subject_id}")
    
    # Проверяем, проходил ли пользователь уже этот тест
    test_id = f"course_entry_{subject_id}"
    test_results = get_test_results(test_id, "student1")  # В реальном приложении здесь будет ID студента
    print(f"DEBUG: Результаты теста: {test_results}")
    
    if test_results and test_results.get("total_questions", 0) > 0:
        # Если тест уже пройден, показываем результаты
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
        print(f"DEBUG: Показываем результаты для предмета: {subject_name}")
        
        # Форматируем результаты
        result_text = format_test_result(test_results, subject_name, "course_entry")
        
        await callback.message.edit_text(
            result_text,
            reply_markup=get_back_to_test_report_kb()
        )
        await state.set_state(TestReportStates.test_result)
    else:
        # Если тест еще не пройден, начинаем его
        print(f"DEBUG: Начинаем тест для предмета: {subject_id}")
        await start_course_entry_test(callback, state, subject_id)

async def start_course_entry_test(callback: CallbackQuery, state: FSMContext, subject_id: str):
    """Начать входной тест курса по выбранному предмету"""
    # Сохраняем информацию о выбранном предмете
    await state.update_data(selected_subject=subject_id)
    
    # Получаем 30 случайных вопросов
    # В реальном приложении здесь будет запрос к базе данных
    test_questions = generate_random_questions(30)
    
    await state.update_data(
        test_started=True,
        test_type="course_entry",
        total_questions=len(test_questions),
        current_question=1,
        correct_answers=0,
        user_answers={},
        test_questions=test_questions,
        topics_progress={}  # Для отслеживания прогресса по темам
    )
    
    # Показываем первый вопрос
    await show_test_question(callback, state, 1)
    await state.set_state(TestReportStates.test_in_progress)

async def show_test_question(callback: CallbackQuery, state: FSMContext, question_number: int):
    """Показать вопрос теста"""
    user_data = await state.get_data()
    test_questions = user_data.get("test_questions", [])
    
    if question_number > len(test_questions):
        # Если вопросы закончились, завершаем тест
        await finish_course_entry_test(callback, state)
        return
    
    question = test_questions[question_number - 1]
    options_text = "\n".join([f"{key}) {value}" for key, value in question["options"].items()])
    
    await callback.message.edit_text(
        f"Вопрос {question_number}/{len(test_questions)}\n\n"
        f"{question['text']}\n\n"
        f"{options_text}",
        reply_markup=get_test_answers_kb()
    )

@router.callback_query(TestReportStates.test_in_progress, F.data.startswith("answer_"))
async def process_test_answer(callback: CallbackQuery, state: FSMContext):
    """Обработка ответа на вопрос теста"""
    selected_answer = callback.data.replace("answer_", "")
    user_data = await state.get_data()
    current_question = user_data.get("current_question", 1)
    test_questions = user_data.get("test_questions", [])
    
    if current_question <= len(test_questions):
        question = test_questions[current_question - 1]
        
        # Проверяем правильность ответа
        is_correct = selected_answer == question["correct"]
        
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
        
        # Если есть следующий вопрос, показываем его
        if next_question <= len(test_questions):
            await show_test_question(callback, state, next_question)
        else:
            # Иначе завершаем тест
            await finish_course_entry_test(callback, state)
    else:
        # Если все вопросы пройдены, завершаем тест
        await finish_course_entry_test(callback, state)

async def finish_course_entry_test(callback: CallbackQuery, state: FSMContext):
    """Завершение входного теста курса и показ результатов"""
    user_data = await state.get_data()
    total_questions = user_data.get("total_questions", 0)
    correct_answers = user_data.get("correct_answers", 0)
    topics_progress = user_data.get("topics_progress", {})
    selected_subject = user_data.get("selected_subject", "chem")
    
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
    
    # Добавляем темы, которые не были проверены
    all_topics = ["Алканы", "Изомерия", "Кислоты", "Циклоалканы"]  # В реальном приложении это будет список всех тем предмета
    for topic in all_topics:
        if topic not in topics_percentages:
            topics_percentages[topic] = None
    
    # Формируем текст с результатами
    result_text = f"📊 Входной тест курса пройден\nРезультат:\n📗 {subject_name}:\n"
    result_text += f"Верных: {correct_answers} / {total_questions}\n"
    
    # Добавляем информацию о каждой теме
    for topic, percentage in topics_percentages.items():
        if percentage is None:
            result_text += f"• {topic} — ❌ Не проверено\n"
        else:
            status = "✅" if percentage >= 80 else "❌" if percentage <= 40 else "⚠️"
            result_text += f"• {topic} — {percentage}% {status}\n"
    
    # Определяем сильные и слабые темы
    strong_topics = [topic for topic, percentage in topics_percentages.items() 
                    if percentage is not None and percentage >= 80]
    weak_topics = [topic for topic, percentage in topics_percentages.items() 
                  if percentage is not None and percentage <= 40]
    
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
    
    await callback.message.edit_text(
        result_text,
        reply_markup=get_back_to_test_report_kb()
    )
    await state.set_state(TestReportStates.test_result)

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

@router.callback_query(TestReportStates.main, F.data == "month_entry_test")
async def choose_month_entry_subject(callback: CallbackQuery, state: FSMContext):
    """Выбор предмета для входного теста месяца"""
    await callback.message.edit_text(
        "📅 Входной тест месяца\n"
        "Выбери предмет, затем месяц курса.\n"
        "Результат определит стартовый % понимания по темам этого месяца.",
        reply_markup=get_test_subjects_kb("month_entry")
    )
    await state.set_state(TestReportStates.month_entry_subject)

@router.callback_query(TestReportStates.month_entry_subject, F.data.startswith("month_entry_sub_"))
async def choose_month_entry_month(callback: CallbackQuery, state: FSMContext):
    """Выбор месяца для входного теста месяца"""
    subject_id = callback.data.replace("month_entry_sub_", "")
    await state.update_data(subject_id=subject_id)
    
    await callback.message.edit_text(
        "Выбери месяц курса:",
        reply_markup=get_month_test_kb("month_entry", subject_id)
    )
    await state.set_state(TestReportStates.month_entry_month)

@router.callback_query(TestReportStates.month_entry_month, F.data.startswith("month_entry_"))
async def show_month_entry_test_result(callback: CallbackQuery, state: FSMContext):
    """Показать результат входного теста месяца"""
    # Получаем данные о выбранном предмете и месяце
    data = callback.data.split("_")
    month = data[-1]
    
    user_data = await state.get_data()
    subject_id = user_data.get("subject_id", "")
    
    # Определяем название предмета
    subject_name = "Химия"  # В реальном приложении это будет определяться по subject_id
    
    # Получаем результаты теста
    test_id = f"month_entry_{subject_id}_{month}"
    test_results = get_test_results(test_id, "student1")  # В реальном приложении здесь будет ID студента
    
    # Форматируем результаты
    result_text = format_test_result(test_results, subject_name, "month_entry", month)
    
    await callback.message.edit_text(
        result_text,
        reply_markup=get_back_to_test_report_kb()
    )
    await state.set_state(TestReportStates.test_result)

@router.callback_query(TestReportStates.main, F.data == "month_control_test")
async def choose_month_control_subject(callback: CallbackQuery, state: FSMContext):
    """Выбор предмета для контрольного теста месяца"""
    await callback.message.edit_text(
        "📅 Контрольный тест месяца\n"
        "Будет сформирован по тем же темам, что ты проходил во входном тесте.\n"
        "Готов узнать, насколько ты прокачал понимание?",
        reply_markup=get_test_subjects_kb("month_control")
    )
    await state.set_state(TestReportStates.month_control_subject)

@router.callback_query(TestReportStates.month_control_subject, F.data.startswith("month_control_sub_"))
async def choose_month_control_month(callback: CallbackQuery, state: FSMContext):
    """Выбор месяца для контрольного теста месяца"""
    subject_id = callback.data.replace("month_control_sub_", "")
    await state.update_data(subject_id=subject_id)
    
    await callback.message.edit_text(
        "Выбери месяц курса:",
        reply_markup=get_month_test_kb("month_control", subject_id)
    )
    await state.set_state(TestReportStates.month_control_month)

@router.callback_query(TestReportStates.month_control_month, F.data.startswith("month_control_"))
async def show_month_control_test_result(callback: CallbackQuery, state: FSMContext):
    """Показать результат контрольного теста месяца"""
    # Получаем данные о выбранном предмете и месяце
    data = callback.data.split("_")
    month = data[-1]
    
    user_data = await state.get_data()
    subject_id = user_data.get("subject_id", "")
    
    # Определяем название предмета
    subject_name = "Химия"  # В реальном приложении это будет определяться по subject_id
    
    # Получаем результаты входного и контрольного тестов
    entry_test_id = f"month_entry_{subject_id}_{month}"
    control_test_id = f"month_control_{subject_id}_{month}"
    
    entry_results = get_test_results(entry_test_id, "student1")  # В реальном приложении здесь будет ID студента
    control_results = get_test_results(control_test_id, "student1")  # В реальном приложении здесь будет ID студента
    
    # Форматируем сравнение результатов
    result_text = format_test_comparison(entry_results, control_results, subject_name, month)
    
    await callback.message.edit_text(
        result_text,
        reply_markup=get_back_to_test_report_kb()
    )
    await state.set_state(TestReportStates.test_result)

@router.callback_query(F.data == "back_to_test_report")
async def back_to_test_report(callback: CallbackQuery, state: FSMContext):
    """Вернуться в меню тест-отчета"""
    await show_test_report_menu(callback, state)

@router.callback_query(F.data.startswith("back_to_month_entry_subjects"))
async def back_to_month_entry_subjects(callback: CallbackQuery, state: FSMContext):
    """Вернуться к выбору предмета для входного теста месяца"""
    await choose_month_entry_subject(callback, state)

@router.callback_query(F.data.startswith("back_to_month_control_subjects"))
async def back_to_month_control_subjects(callback: CallbackQuery, state: FSMContext):
    """Вернуться к выбору предмета для контрольного теста месяца"""
    await choose_month_control_subject(callback, state)