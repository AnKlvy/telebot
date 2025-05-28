from typing import Dict, List, Tuple, Optional

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from common.analytics.keyboards import get_back_to_analytics_kb


def get_student_topics_stats(student_id: str) -> Dict:
    """
    Получить статистику по темам для конкретного ученика
    
    Args:
        student_id: ID ученика
        
    Returns:
        Dict: Словарь с данными о студенте и его прогрессе по темам
    """
    # В реальном приложении здесь будет запрос к базе данных
    student_data = {
        "student1": {
            "name": "Мадияр Сапаров",
            "topics": {
                "Алканы": 80,
                "Изомерия": 45,
                "Кислоты": 70
            }
        },
        "student2": {
            "name": "Аружан Ахметова",
            "topics": {
                "Алканы": 90,
                "Изомерия": 33,
                "Кислоты": 60
            }
        },
        "student3": {
            "name": "Диана Нурланова",
            "topics": {
                "Алканы": 85,
                "Изомерия": 40,
                "Кислоты": 75
            }
        },
        "student4": {
            "name": "Арман Сериков",
            "topics": {
                "Алканы": 75,
                "Изомерия": 30,
                "Кислоты": 50
            }
        }
    }
    
    return student_data.get(student_id, {"name": "Неизвестный ученик", "topics": {}})

def get_group_stats(group_id: str) -> Dict:
    """
    Получить статистику по группе
    
    Args:
        group_id: ID группы
        
    Returns:
        Dict: Словарь с данными о группе и статистике
    """
    # В реальном приложении здесь будет запрос к базе данных
    group_data = {
        "group1": {
            "name": "Интенсив. География",
            "subject": "Химия",
            "homework_completion": 75,
            "topics": {
                "Алканы": 82,
                "Изомерия": 37,
                "Кислоты": 66
            },
            "rating": [
                {"name": "Аружан", "points": 870},
                {"name": "Диана", "points": 800},
                {"name": "Мадияр", "points": 780}
            ]
        },
        "group2": {
            "name": "Интенсив. Математика",
            "subject": "Химия",
            "homework_completion": 80,
            "topics": {
                "Алканы": 78,
                "Изомерия": 42,
                "Кислоты": 70
            },
            "rating": [
                {"name": "Арман", "points": 850},
                {"name": "Алия", "points": 820},
                {"name": "Диас", "points": 790}
            ]
        }
    }
    
    return group_data.get(group_id, {
        "name": "Неизвестная группа",
        "subject": "Неизвестный предмет",
        "homework_completion": 0,
        "topics": {},
        "rating": []
    })

def format_student_topics_stats(student_data: Dict) -> str:
    """
    Форматировать статистику по темам ученика в текстовый вид
    
    Args:
        student_data: Данные ученика
        
    Returns:
        str: Отформатированный текст со статистикой
    """
    # Определяем сильные и слабые темы
    strong_topics = [topic for topic, percentage in student_data["topics"].items() 
                    if percentage >= 80]
    weak_topics = [topic for topic, percentage in student_data["topics"].items() 
                  if percentage <= 40]
    
    # Формируем текст с результатами
    result_text = f"📌 {student_data['name']}\n"
    result_text += "📈 % понимания по микротемам:\n"
    
    # Добавляем информацию о каждой теме
    for topic, percentage in student_data["topics"].items():
        status = "✅" if percentage >= 80 else "❌" if percentage <= 40 else "⚠️"
        result_text += f"• {topic} — {percentage}% {status}\n"
    
    # Добавляем информацию о сильных и слабых темах в более наглядном формате
    if strong_topics:
        result_text += "\n🟢 Сильные темы (≥80%):\n"
        for topic in strong_topics:
            result_text += f"• {topic}\n"
    
    if weak_topics:
        result_text += "\n🔴 Слабые темы (≤40%):\n"
        for topic in weak_topics:
            result_text += f"• {topic}\n"
    
    return result_text

def format_group_stats(group_data: Dict) -> str:
    """
    Форматировать статистику по группе в текстовый вид
    
    Args:
        group_data: Данные группы
        
    Returns:
        str: Отформатированный текст со статистикой
    """
    # Формируем текст с результатами
    result_text = f"📗 {group_data['subject']}\n"
    result_text += f"📊 Средний % выполнения ДЗ: {group_data['homework_completion']}%\n"
    result_text += "📈 Средний % понимания по микротемам:\n"
    
    # Добавляем информацию о каждой теме
    for topic, percentage in group_data["topics"].items():
        result_text += f"• {topic} — {percentage}%\n"
    
    # Добавляем рейтинг по баллам
    if group_data["rating"]:
        result_text += "\n📋 Рейтинг по баллам:\n"
        for i, student in enumerate(group_data["rating"], 1):
            result_text += f"{i}. {student['name']} — {student['points']} баллов\n"
    
    return result_text

def get_test_results(test_id: str, student_id: str) -> Dict:
    """
    Получить результаты теста для студента
    
    Args:
        test_id: Идентификатор теста
        student_id: Идентификатор студента
        
    Returns:
        Dict: Словарь с результатами теста
    """
    print(f"DEBUG: Запрос результатов теста: {test_id} для студента: {student_id}")
    
    # В реальном приложении здесь будет запрос к базе данных
    # Для примера используем фиксированные значения
    test_results = {
        "course_entry_chem": {
            "total_questions": 30,
            "correct_answers": 15,
            "topics_progress": {
                "Алканы": 90,
                "Изомерия": 33,
                "Кислоты": 60,
                "Циклоалканы": None  # None означает, что тема не проверена
            }
        },
        "course_entry_kz": {
            "total_questions": 30,
            "correct_answers": 20,
            "topics_progress": {
                "Древняя история": 80,
                "Средневековье": 60,
                "Новое время": 40,
                "Новейшая история": None  # None означает, что тема не проверена
            }
        },
        "month_entry_chem_1": {
            "total_questions": 30,
            "correct_answers": 15,
            "topics_progress": {
                "Алканы": 60,
                "Изомерия": 33,
                "Кислоты": 60
            }
        },
        "month_control_chem_1": {
            "total_questions": 30,
            "correct_answers": 20,
            "topics_progress": {
                "Алканы": 90,
                "Изомерия": 45,
                "Кислоты": 100
            }
        }
    }
    
    result = test_results.get(test_id, {
        "total_questions": 0,
        "correct_answers": 0,
        "topics_progress": {}
    })
    
    print(f"DEBUG: Возвращаемые результаты: {result}")
    return result

def format_test_result(test_results: Dict, subject_name: str, test_type: str, month: str = None) -> str:
    """
    Форматировать результаты теста в текстовый вид
    
    Args:
        test_results: Результаты теста
        subject_name: Название предмета
        test_type: Тип теста (course_entry, month_entry, month_control)
        month: Месяц (опционально)
        
    Returns:
        str: Отформатированный текст с результатами
    """
    # Определяем заголовок в зависимости от типа теста
    if test_type == "course_entry":
        result_text = f"📊 Входной тест курса пройден\nРезультат:\n📗 {subject_name}:\n"
    elif test_type == "month_entry":
        result_text = f"📊 Входной тест месяца {month} курса пройден\nРезультат:\n📗 {subject_name}:\n"
    elif test_type == "month_control":
        result_text = f"📊 Контрольный тест месяца {month} курса пройден\nРезультат:\n📗 {subject_name}:\n"
    else:
        result_text = f"📊 Тест пройден\nРезультат:\n📗 {subject_name}:\n"
    
    # Добавляем информацию о количестве правильных ответов
    result_text += f"Верных: {test_results['correct_answers']} / {test_results['total_questions']}\n"
    
    # Добавляем информацию о каждой теме
    for topic, percentage in test_results["topics_progress"].items():
        if percentage is None:
            result_text += f"• {topic} — ❌ Не проверено\n"
        else:
            status = "✅" if percentage >= 80 else "❌" if percentage <= 40 else "⚠️"
            result_text += f"• {topic} — {percentage}% {status}\n"
    
    # Определяем сильные и слабые темы
    strong_topics = [topic for topic, percentage in test_results["topics_progress"].items() 
                    if percentage is not None and percentage >= 80]
    weak_topics = [topic for topic, percentage in test_results["topics_progress"].items() 
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
    
    return result_text

def format_test_comparison(entry_results: Dict, control_results: Dict, subject_name: str, month: str) -> str:
    """
    Форматировать сравнение входного и контрольного тестов
    
    Args:
        entry_results: Результаты входного теста
        control_results: Результаты контрольного теста
        subject_name: Название предмета
        month: Месяц
        
    Returns:
        str: Отформатированный текст со сравнением
    """
    # Вычисляем общий прирост
    entry_topics = entry_results["topics_progress"]
    control_topics = control_results["topics_progress"]
    
    if entry_topics and control_topics:
        entry_avg = sum(entry_topics.values()) / len(entry_topics)
        control_avg = sum(control_topics.values()) / len(control_topics)
        growth = int(control_avg - entry_avg)
    else:
        growth = 0
    
    # Формируем текст с результатами
    result_text = f"🧾 Сравнение входного и контрольного теста месяца по предмету:\n📗 {subject_name}:\n"
    result_text += f"Верных: {entry_results['correct_answers']} / {entry_results['total_questions']} → {control_results['correct_answers']} / {control_results['total_questions']}\n"
    
    # Добавляем информацию о каждой теме
    for topic in entry_topics:
        if topic in control_topics:
            entry_percentage = entry_topics[topic]
            control_percentage = control_topics[topic]
            result_text += f"• {topic} — {entry_percentage}% → {control_percentage}%\n"
    
    result_text += f"\n📈 Общий прирост: +{growth}%\n"
    
    # Определяем сильные и слабые темы по результатам контрольного теста
    strong_topics = [topic for topic, percentage in control_topics.items() 
                    if percentage is not None and percentage >= 80]
    weak_topics = [topic for topic, percentage in control_topics.items() 
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
    
    return result_text

def get_subject_stats(subject_id: str) -> dict:
    """
    Получить статистику по предмету

    Args:
        subject_id: ID предмета

    Returns:
        dict: Данные о статистике предмета
    """
    # В реальном приложении здесь будет запрос к базе данных
    # Для примера возвращаем тестовые данные
    return {
        "subject_id": subject_id,
        "name": "Химия",
        "groups": [
            {
                "group_id": "group1",
                "name": "Интенсив. География",
                "homework_completion": 75,
                "topics": {
                    "Алканы": 82,
                    "Изомерия": 37,
                    "Кислоты": 66
                },
                "rating": [
                    {"name": "Аружан", "points": 870},
                    {"name": "Диана", "points": 800},
                    {"name": "Мадияр", "points": 780}
                ]
            },
            {
                "group_id": "group2",
                "name": "Интенсив. Математика",
                "homework_completion": 80,
                "topics": {
                    "Алканы": 78,
                    "Изомерия": 42,
                    "Кислоты": 70
                },
                "rating": [
                    {"name": "Арман", "points": 850},
                    {"name": "Алия", "points": 820},
                    {"name": "Диас", "points": 790}
                ]
            }
        ]
    }

def get_general_stats() -> dict:
    """
    Получить общую статистику по всем предметам
    
    Returns:
        dict: Общие данные статистики
    """
    # В реальном приложении здесь будет запрос к базе данных
    # Для примера возвращаем тестовые данные
    return {
        "total_students": 450,
        "active_students": 380,
        "total_groups": 15,
        "subjects": [
            {"name": "Математика", "average_score": 78.5, "completion_rate": 82.3},
            {"name": "Физика", "average_score": 75.2, "completion_rate": 79.8},
            {"name": "Химия", "average_score": 81.7, "completion_rate": 85.4},
            {"name": "Биология", "average_score": 83.1, "completion_rate": 87.2}
        ],
        "monthly_progress": {
            "Январь": 75.2,
            "Февраль": 78.5,
            "Март": 80.1,
            "Апрель": 82.3
        }
    }

def format_subject_stats(subject_data: dict) -> str:
    """
    Форматировать статистику по предмету в текстовый вид
    
    Args:
        subject_data: Данные о предмете
        
    Returns:
        str: Отформатированный текст со статистикой
    """
    result_text = f"📊 Статистика по предмету: {subject_data['name']}\n\n"
    
    # Добавляем информацию о группах
    result_text += "👨‍👩‍👧‍👦 Группы:\n"
    for group in subject_data["groups"]:
        result_text += f"• {group['name']} - выполнение ДЗ: {group['homework_completion']}%\n"
    
    # Добавляем информацию о средних показателях по темам
    result_text += "\n📈 Средние показатели по темам:\n"
    
    # Собираем все темы из всех групп
    all_topics = {}
    for group in subject_data["groups"]:
        for topic, percentage in group["topics"].items():
            if topic in all_topics:
                all_topics[topic].append(percentage)
            else:
                all_topics[topic] = [percentage]
    
    # Вычисляем средние значения и выводим
    for topic, percentages in all_topics.items():
        avg_percentage = sum(percentages) / len(percentages)
        result_text += f"• {topic} — {avg_percentage:.1f}%\n"
    
    return result_text

def format_general_stats(general_data: dict) -> str:
    """
    Форматировать общую статистику в текстовый вид
    
    Args:
        general_data: Общие данные статистики
        
    Returns:
        str: Отформатированный текст со статистикой
    """
    result_text = "📊 Общая статистика\n\n"
    
    # Добавляем общую информацию
    result_text += f"👥 Всего учеников: {general_data['total_students']}\n"
    result_text += f"👤 Активных учеников: {general_data['active_students']} ({general_data['active_students']/general_data['total_students']*100:.1f}%)\n"
    result_text += f"👨‍👩‍👧‍👦 Всего групп: {general_data['total_groups']}\n\n"
    
    # Добавляем информацию о предметах
    result_text += "📚 Статистика по предметам:\n"
    for subject in general_data["subjects"]:
        result_text += f"• {subject['name']} — средний балл: {subject['average_score']}, выполнение: {subject['completion_rate']}%\n"
    
    # Добавляем информацию о прогрессе по месяцам
    result_text += "\n📅 Прогресс по месяцам:\n"
    for month, progress in general_data["monthly_progress"].items():
        result_text += f"• {month} — {progress}%\n"
    
    return result_text


async def show_student_analytics(callback: CallbackQuery, state: FSMContext, role: str):
    """
    Базовый обработчик для показа статистики по ученику

    Args:
        callback: Объект CallbackQuery
        state: Контекст состояния FSM
        role: Роль пользователя (curator)
    """
    student_id = await check_if_id_in_callback_data("analytics_student_",callback, state, "student")


    # Получаем данные о студенте из общего компонента
    student_data = get_student_topics_stats(student_id)

    # Форматируем статистику в текст
    result_text = format_student_topics_stats(student_data)

    await callback.message.edit_text(
        result_text,
        reply_markup=get_back_to_analytics_kb()
    )
    # Удаляем установку состояния


async def show_group_analytics(callback: CallbackQuery, state: FSMContext, role: str):
    """
    Базовый обработчик для показа статистики по группе

    Args:
        callback: Объект CallbackQuery
        state: Контекст состояния FSM
        role: Роль пользователя (curator)
    """
    group_id = await check_if_id_in_callback_data("analytics_group_",callback, state, "group")

    # Получаем данные о группе из общего компонента
    group_data = get_group_stats(group_id)

    # Форматируем статистику в текст
    result_text = format_group_stats(group_data)

    await callback.message.edit_text(
        result_text,
        reply_markup=get_back_to_analytics_kb()
    )


async def check_if_id_in_callback_data(callback_starts_with: str, callback: CallbackQuery, state: FSMContext, id_type)-> str:
    # Проверяем, является ли callback.data ID группы или это кнопка "назад"
    if callback.data.startswith(callback_starts_with):
        id = callback.data.replace(callback_starts_with, "")
        print(f"{id_type}_id: ", id)
        await state.update_data(**{id_type:id})
    else:
        # Если это кнопка "назад" или другой callback, берем ID из состояния
        user_data = await state.get_data()
        id = user_data.get(id_type)
        print(f"Using saved {id_type}_id: ", id)
    return id
