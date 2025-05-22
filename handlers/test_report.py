from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from keyboards.test_report import (
    get_test_report_menu_kb, 
    get_test_subjects_kb, 
    get_month_test_kb,
    get_back_to_test_report_kb
)

router = Router()

class TestReportStates(StatesGroup):
    main = State()
    course_entry_subject = State()
    month_entry_subject = State()
    month_entry_month = State()
    month_control_subject = State()
    month_control_month = State()
    test_result = State()

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
async def show_course_entry_test_result(callback: CallbackQuery, state: FSMContext):
    """Показать результат входного теста курса"""
    subject_id = callback.data.replace("course_entry_sub_", "")
    
    # Определяем название предмета
    subject_name = "Химия"  # В реальном приложении это будет определяться по subject_id
    
    # В реальном приложении здесь будет логика проверки, проходил ли пользователь тест
    # и получения результатов из базы данных
    # Для примера используем фиксированные значения
    
    # Пример данных о результатах теста
    test_results = {
        "total_questions": 30,
        "correct_answers": 15,
        "topics_progress": {
            "Алканы": 90,
            "Изомерия": 33,
            "Кислоты": 60,
            "Циклоалканы": None  # None означает, что тема не проверена
        }
    }
    
    # Формируем текст с результатами
    result_text = f"📊 Входной тест курса пройден\nРезультат:\n📗 {subject_name}:\n"
    result_text += f"Верных: {test_results['correct_answers']} / {test_results['total_questions']}\n"
    
    # Добавляем информацию о каждой теме
    for topic, percentage in test_results["topics_progress"].items():
        if percentage is None:
            result_text += f"• {topic} — ❌ Не проверено\n"
        else:
            result_text += f"• {topic} — {percentage}%\n"
    
    await callback.message.edit_text(
        result_text,
        reply_markup=get_back_to_test_report_kb()
    )
    await state.set_state(TestReportStates.test_result)

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
    
    # В реальном приложении здесь будет логика проверки, проходил ли пользователь тест
    # и получения результатов из базы данных
    # Для примера используем фиксированные значения
    
    # Пример данных о результатах теста
    test_results = {
        "total_questions": 30,
        "correct_answers": 15,
        "topics_progress": {
            "Алканы": 60,
            "Изомерия": 33,
            "Кислоты": 60
        }
    }
    
    # Определяем сильные и слабые темы
    strong_topics = [topic for topic, percentage in test_results["topics_progress"].items() 
                    if percentage is not None and percentage >= 80]
    weak_topics = [topic for topic, percentage in test_results["topics_progress"].items() 
                  if percentage is not None and percentage <= 40]
    
    # Формируем текст с результатами
    result_text = f"📊 Входной тест месяца {month} курса пройден\nРезультат:\n📗 {subject_name}:\n"
    result_text += f"Верных: {test_results['correct_answers']} / {test_results['total_questions']}\n"
    
    # Добавляем информацию о каждой теме
    for topic, percentage in test_results["topics_progress"].items():
        result_text += f"• {topic} — {percentage}%\n"
    
    # Добавляем информацию о сильных и слабых темах
    if strong_topics:
        result_text += "\n🟢 Сильные темы (≥80%):\n"
        for topic in strong_topics:
            result_text += f"• {topic}\n"
    
    if weak_topics:
        result_text += "\n🔴 Слабые темы (≤40%):\n"
        for topic in weak_topics:
            result_text += f"• {topic}\n"
    
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
    
    # В реальном приложении здесь будет логика проверки, проходил ли пользователь тест
    # и получения результатов из базы данных
    # Для примера используем фиксированные значения
    
    # Пример данных о результатах входного и контрольного тестов
    test_results = {
        "entry": {
            "total_questions": 30,
            "correct_answers": 15,
            "topics_progress": {
                "Алканы": 60,
                "Изомерия": 33,
                "Кислоты": 60
            }
        },
        "control": {
            "total_questions": 30,
            "correct_answers": 20,
            "topics_progress": {
                "Алканы": 90,
                "Изомерия": 45,
                "Кислоты": 100
            }
        }
    }
    
    # Определяем сильные и слабые темы по результатам контрольного теста
    strong_topics = [topic for topic, percentage in test_results["control"]["topics_progress"].items() 
                    if percentage is not None and percentage >= 80]
    weak_topics = [topic for topic, percentage in test_results["control"]["topics_progress"].items() 
                  if percentage is not None and percentage <= 40]
    
    # Вычисляем общий прирост
    entry_avg = sum(test_results["entry"]["topics_progress"].values()) / len(test_results["entry"]["topics_progress"])
    control_avg = sum(test_results["control"]["topics_progress"].values()) / len(test_results["control"]["topics_progress"])
    growth = int(control_avg - entry_avg)
    
    # Формируем текст с результатами
    result_text = f"🧾 Сравнение входного и контрольного теста месяца по предмету:\n📗 {subject_name}:\n"
    result_text += f"Верных: {test_results['entry']['correct_answers']} / {test_results['entry']['total_questions']} → {test_results['control']['correct_answers']} / {test_results['control']['total_questions']}\n"
    
    # Добавляем информацию о каждой теме
    for topic in test_results["entry"]["topics_progress"]:
        entry_percentage = test_results["entry"]["topics_progress"][topic]
        control_percentage = test_results["control"]["topics_progress"][topic]
        result_text += f"• {topic} — {entry_percentage}% → {control_percentage}%\n"
    
    result_text += f"\n📈 Общий прирост: +{growth}%\n"
    
    # Добавляем информацию о сильных и слабых темах
    if strong_topics:
        result_text += "\n🟢 Сильные темы (≥80%):\n"
        for topic in strong_topics:
            result_text += f"• {topic}\n"
    
    if weak_topics:
        result_text += "\n🔴 Слабые темы (≤40%):\n"
        for topic in weak_topics:
            result_text += f"• {topic}\n"
    
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