from typing import Dict, List, Tuple, Optional

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
    Получить результаты теста для конкретного ученика
    
    Args:
        test_id: ID теста
        student_id: ID ученика
        
    Returns:
        Dict: Словарь с результатами теста
    """
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
    
    return test_results.get(test_id, {
        "total_questions": 0,
        "correct_answers": 0,
        "topics_progress": {}
    })

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
