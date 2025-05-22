from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from keyboards.trial_ent import (
    get_trial_ent_start_kb,
    get_required_subjects_kb,
    get_profile_subjects_kb,
    get_second_profile_subject_kb,
    get_test_answers_kb,
    get_after_trial_ent_kb,
    get_analytics_subjects_kb,
    get_back_to_analytics_kb
)
from .test_logic import process_test_answer

router = Router()

class TrialEntStates(StatesGroup):
    main = State()
    required_subjects = State()
    profile_subjects = State()
    second_profile_subject = State()
    test_in_progress = State()
    results = State()
    analytics_subjects = State()
    subject_analytics = State()

@router.callback_query(F.data == "trial_ent")
async def show_trial_ent_menu(callback: CallbackQuery, state: FSMContext):
    """Показать меню пробного ЕНТ"""
    await callback.message.edit_text(
        "Это симуляция ЕНТ: 130 баллов (за исключением грамотности чтения).\n"
        "Для начала выбери обязательные и профильные предметы",
        reply_markup=get_trial_ent_start_kb()
    )
    await state.set_state(TrialEntStates.main)

@router.callback_query(TrialEntStates.main, F.data == "start_trial_ent")
async def choose_required_subjects(callback: CallbackQuery, state: FSMContext):
    """Выбор обязательных предметов"""
    await callback.message.edit_text(
        "Обязательные предметы:",
        reply_markup=get_required_subjects_kb()
    )
    await state.set_state(TrialEntStates.required_subjects)

@router.callback_query(TrialEntStates.required_subjects, F.data.startswith("req_sub_"))
async def choose_profile_subjects(callback: CallbackQuery, state: FSMContext):
    """Выбор профильных предметов"""
    required_subjects = callback.data.replace("req_sub_", "")
    
    # Сохраняем выбранные обязательные предметы
    if required_subjects == "kz":
        selected_subjects = ["kz"]
    elif required_subjects == "mathlit":
        selected_subjects = ["mathlit"]
    else:  # both
        selected_subjects = ["kz", "mathlit"]
    
    await state.update_data(required_subjects=selected_subjects)
    
    await callback.message.edit_text(
        "Профильные предметы:",
        reply_markup=get_profile_subjects_kb()
    )
    await state.set_state(TrialEntStates.profile_subjects)

@router.callback_query(TrialEntStates.profile_subjects, F.data.startswith("prof_sub_"))
async def process_profile_subject(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора профильного предмета"""
    profile_subject = callback.data
    
    if profile_subject == "prof_sub_none":
        # Если выбрано "Нет профильных предметов", переходим к началу теста
        await state.update_data(profile_subjects=[])
        await start_trial_ent_test(callback, state)
    else:
        # Сохраняем первый выбранный профильный предмет
        await state.update_data(first_profile_subject=profile_subject)
        
        # Предлагаем выбрать второй профильный предмет
        await callback.message.edit_text(
            "Выберите второй профильный предмет:",
            reply_markup=get_second_profile_subject_kb(profile_subject)
        )
        await state.set_state(TrialEntStates.second_profile_subject)

@router.callback_query(TrialEntStates.second_profile_subject, F.data.startswith("second_prof_sub_"))
async def process_second_profile_subject(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора второго профильного предмета"""
    second_profile_subject = callback.data.replace("second_", "")
    
    # Получаем данные о первом выбранном профильном предмете
    user_data = await state.get_data()
    first_profile_subject = user_data.get("first_profile_subject", "")
    
    # Сохраняем оба профильных предмета
    profile_subjects = [
        first_profile_subject.replace("prof_sub_", ""),
        second_profile_subject.replace("prof_sub_", "")
    ]
    await state.update_data(profile_subjects=profile_subjects)
    
    # Переходим к началу теста
    await start_trial_ent_test(callback, state)

async def start_trial_ent_test(callback: CallbackQuery, state: FSMContext):
    """Начало пробного ЕНТ"""
    user_data = await state.get_data()
    required_subjects = user_data.get("required_subjects", [])
    profile_subjects = user_data.get("profile_subjects", [])
    
    # Формируем список всех выбранных предметов
    all_subjects = required_subjects + profile_subjects
    
    # Определяем общее количество вопросов
    total_questions = 0
    if "kz" in required_subjects:
        total_questions += 20  # История Казахстана - 20 вопросов
    if "mathlit" in required_subjects:
        total_questions += 10  # Математическая грамотность - 10 вопросов
    for _ in profile_subjects:
        total_questions += 50  # Каждый профильный предмет - 50 вопросов
    
    # Сохраняем информацию для последующего использования
    await state.update_data(
        test_started=True,
        total_questions=total_questions,
        current_question=1,
        current_subject_index=0,
        current_subject=all_subjects[0] if all_subjects else None,
        subject_questions_left={
            "kz": 20 if "kz" in required_subjects else 0,
            "mathlit": 10 if "mathlit" in required_subjects else 0,
            **{subject: 50 for subject in profile_subjects}
        },
        correct_answers={subject: 0 for subject in all_subjects},
        all_subjects=all_subjects
    )
    
    # Показываем первый вопрос
    await show_next_question(callback, state)
    await state.set_state(TrialEntStates.test_in_progress)

async def show_next_question(callback: CallbackQuery, state: FSMContext):
    """Показать следующий вопрос теста"""
    user_data = await state.get_data()
    current_subject = user_data.get("current_subject")
    subject_questions_left = user_data.get("subject_questions_left", {})
    current_question = user_data.get("current_question", 1)
    total_questions = user_data.get("total_questions", 0)
    
    # Проверяем, остались ли вопросы по текущему предмету
    if current_subject and subject_questions_left.get(current_subject, 0) > 0:
        # Генерируем вопрос для текущего предмета
        # В реальном приложении здесь будет логика получения вопроса из базы данных
        
        # Определяем название предмета для отображения
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
        subject_name = subject_names.get(current_subject, "")
        
        # Пример вопроса (в реальном приложении будет загружаться из БД)
        question_text = f"Вопрос по предмету {subject_name}"
        options = {
            "A": "Вариант A",
            "B": "Вариант B",
            "C": "Вариант C",
            "D": "Вариант D"
        }
        
        options_text = "\n".join([f"{key}) {value}" for key, value in options.items()])
        
        await callback.message.edit_text(
            f"Вопрос {current_question}/{total_questions}\n"
            f"Предмет: {subject_name}\n\n"
            f"{question_text}\n\n"
            f"{options_text}",
            reply_markup=get_test_answers_kb()
        )
    else:
        # Если вопросы по текущему предмету закончились, переходим к следующему предмету
        all_subjects = user_data.get("all_subjects", [])
        current_subject_index = user_data.get("current_subject_index", 0)
        
        # Проверяем, есть ли еще предметы
        if current_subject_index + 1 < len(all_subjects):
            # Переходим к следующему предмету
            next_subject_index = current_subject_index + 1
            next_subject = all_subjects[next_subject_index]
            
            await state.update_data(
                current_subject_index=next_subject_index,
                current_subject=next_subject
            )
            
            # Показываем вопрос по новому предмету
            await show_next_question(callback, state)
        else:
            # Если все предметы пройдены, завершаем тест
            await finish_trial_ent(callback, state)

@router.callback_query(TrialEntStates.test_in_progress, F.data.startswith("answer_"))
async def process_answer(callback: CallbackQuery, state: FSMContext):
    """Обработка ответа на вопрос теста"""
    selected_answer = callback.data.replace("answer_", "")
    user_data = await state.get_data()
    current_subject = user_data.get("current_subject")
    subject_questions_left = user_data.get("subject_questions_left", {})
    correct_answers = user_data.get("correct_answers", {})
    current_question = user_data.get("current_question", 1)
    
    # В реальном приложении здесь будет логика проверки правильности ответа
    # Для примера считаем, что ответ правильный с вероятностью 70%
    import random
    is_correct = random.random() < 0.7
    
    # Обновляем счетчики
    if is_correct:
        correct_answers[current_subject] = correct_answers.get(current_subject, 0) + 1
    
    subject_questions_left[current_subject] = subject_questions_left.get(current_subject, 0) - 1
    
    # Обновляем данные состояния
    await state.update_data(
        current_question=current_question + 1,
        subject_questions_left=subject_questions_left,
        correct_answers=correct_answers
    )
    
    # Показываем следующий вопрос
    await show_next_question(callback, state)

async def finish_trial_ent(callback: CallbackQuery, state: FSMContext):
    """Завершение пробного ЕНТ и показ результатов"""
    user_data = await state.get_data()
    required_subjects = user_data.get("required_subjects", [])
    profile_subjects = user_data.get("profile_subjects", [])
    correct_answers = user_data.get("correct_answers", {})
    
    # Определяем названия предметов для отображения
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
    
    # Определяем максимальное количество баллов для каждого предмета
    max_points = {
        "kz": 20,
        "mathlit": 10,
        **{subject: 50 for subject in profile_subjects}
    }
    
    # Вычисляем общее количество баллов
    total_correct = sum(correct_answers.values())
    total_max = sum(max_points.get(subject, 0) for subject in required_subjects + profile_subjects)
    
    # Формируем текст с результатами
    result_text = f"🧾 Верных баллов: {total_correct}/{total_max}\n"
    
    # Добавляем информацию о каждом предмете
    for subject in required_subjects + profile_subjects:
        subject_name = subject_names.get(subject, "")
        subject_correct = correct_answers.get(subject, 0)
        subject_max = max_points.get(subject, 0)
        result_text += f"🧾 Верных баллов по {subject_name}: {subject_correct}/{subject_max}\n"
    
    result_text += "\nХочешь посмотреть свою аналитику по темам?"
    
    # Сохраняем результаты для последующего использования
    await state.update_data(
        test_results={
            "total_correct": total_correct,
            "total_max": total_max,
            "subject_results": {subject: correct_answers.get(subject, 0) for subject in required_subjects + profile_subjects}
        }
    )
    
    await callback.message.edit_text(
        result_text,
        reply_markup=get_after_trial_ent_kb()
    )
    await state.set_state(TrialEntStates.results)

@router.callback_query(TrialEntStates.results, F.data == "view_analytics")
async def show_analytics_subjects(callback: CallbackQuery, state: FSMContext):
    """Показать список предметов для просмотра аналитики"""
    user_data = await state.get_data()
    required_subjects = user_data.get("required_subjects", [])
    profile_subjects = user_data.get("profile_subjects", [])
    
    # Формируем список всех предметов, по которым проходил тест
    all_subjects = required_subjects + profile_subjects
    
    await callback.message.edit_text(
        "Выбери предмет",
        reply_markup=get_analytics_subjects_kb(all_subjects)
    )
    await state.set_state(TrialEntStates.analytics_subjects)

@router.callback_query(TrialEntStates.analytics_subjects, F.data.startswith("analytics_"))
async def show_subject_analytics(callback: CallbackQuery, state: FSMContext):
    """Показать аналитику по выбранному предмету"""
    subject_id = callback.data.replace("analytics_", "")
    
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
    subject_name = subject_names.get(subject_id, "")
    
    # Получаем результаты теста
    user_data = await state.get_data()
    test_results = user_data.get("test_results", {})
    subject_results = test_results.get("subject_results", {})
    subject_correct = subject_results.get(subject_id, 0)
    
    # Определяем максимальное количество баллов для предмета
    max_points = 20 if subject_id == "kz" else 10 if subject_id == "mathlit" else 50
    
    # В реальном приложении здесь будет логика получения аналитики по темам из базы данных
    # Для примера используем фиксированные значения
    topics_analytics = {
        "Алканы": 90,
        "Изомерия": 33,
        "Кислоты": 100
    }
    
    # Определяем сильные и слабые темы
    strong_topics = [topic for topic, percentage in topics_analytics.items() 
                    if percentage is not None and percentage >= 80]
    weak_topics = [topic for topic, percentage in topics_analytics.items() 
                  if percentage is not None and percentage <= 40]
    
    # Формируем текст с аналитикой
    analytics_text = f"Твоя аналитика по предмету {subject_name} по пробному ЕНТ:\n"
    analytics_text += f"🧾 Верных баллов по {subject_name}: {subject_correct}/{max_points}\n"
    
    # Добавляем информацию о каждой теме
    for topic, percentage in topics_analytics.items():
        analytics_text += f"• {topic} — {percentage}%\n"
    
    # Добавляем информацию о сильных и слабых темах
    if strong_topics:
        analytics_text += "\n🟢 Сильные темы (≥80%):\n"
        for topic in strong_topics:
            analytics_text += f"• {topic}\n"
    
    if weak_topics:
        analytics_text += "\n🔴 Слабые темы (≤40%):\n"
        for topic in weak_topics:
            analytics_text += f"• {topic}\n"
    
    await callback.message.edit_text(
        analytics_text,
        reply_markup=get_back_to_analytics_kb()
    )
    await state.set_state(TrialEntStates.subject_analytics)

@router.callback_query(TrialEntStates.results, F.data == "retry_trial_ent")
async def retry_trial_ent(callback: CallbackQuery, state: FSMContext):
    """Пройти пробный ЕНТ еще раз"""
    await show_trial_ent_menu(callback, state)

@router.callback_query(F.data == "back_to_trial_ent")
async def back_to_trial_ent(callback: CallbackQuery, state: FSMContext):
    """Вернуться в меню пробного ЕНТ"""
    await show_trial_ent_menu(callback, state)

@router.callback_query(F.data == "back_to_required_subjects")
async def back_to_required_subjects(callback: CallbackQuery, state: FSMContext):
    """Вернуться к выбору обязательных предметов"""
    await choose_required_subjects(callback, state)

@router.callback_query(F.data == "back_to_profile_subjects")
async def back_to_profile_subjects(callback: CallbackQuery, state: FSMContext):
    """Вернуться к выбору профильных предметов"""
    await choose_profile_subjects(callback, state)

@router.callback_query(F.data == "back_to_trial_ent_results")
async def back_to_trial_ent_results(callback: CallbackQuery, state: FSMContext):
    """Вернуться к результатам пробного ЕНТ"""
    # Получаем сохраненные результаты теста
    user_data = await state.get_data()
    test_results = user_data.get("test_results", {})
    total_correct = test_results.get("total_correct", 0)
    total_max = test_results.get("total_max", 0)
    subject_results = test_results.get("subject_results", {})
    
    # Определяем названия предметов для отображения
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
    
    # Формируем текст с результатами
    result_text = f"🧾 Верных баллов: {total_correct}/{total_max}\n"
    
    # Добавляем информацию о каждом предмете
    for subject, correct in subject_results.items():
        subject_name = subject_names.get(subject, "")
        subject_max = 20 if subject == "kz" else 10 if subject == "mathlit" else 50
        result_text += f"🧾 Верных баллов по {subject_name}: {correct}/{subject_max}\n"
    
    result_text += "\nХочешь посмотреть свою аналитику по темам?"
    
    await callback.message.edit_text(
        result_text,
        reply_markup=get_after_trial_ent_kb()
    )
    await state.set_state(TrialEntStates.results)

@router.callback_query(F.data == "back_to_analytics_subjects")
async def back_to_analytics_subjects(callback: CallbackQuery, state: FSMContext):
    """Вернуться к выбору предмета для аналитики"""
    await show_analytics_subjects(callback, state)