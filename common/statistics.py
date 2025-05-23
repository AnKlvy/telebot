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