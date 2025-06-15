#!/usr/bin/env python3
"""
Очистка результатов ДЗ и создание новых разнообразных данных
"""
import asyncio
import sys
import os

# Добавляем корневую директорию в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import init_database
from database.repositories import (
    HomeworkResultRepository,
    QuestionResultRepository,
    StudentRepository
)


async def clear_and_recreate_homework_results():
    """Очищаем старые результаты и создаем новые разнообразные"""
    print("🧹 Очистка старых результатов ДЗ...")
    
    await init_database()
    
    # Очищаем все результаты
    from database.database import get_db_session
    from sqlalchemy import text
    
    async with get_db_session() as session:
        # Удаляем результаты вопросов
        await session.execute(text("DELETE FROM question_results"))
        print("   ✅ Удалены результаты вопросов")
        
        # Удаляем результаты ДЗ
        await session.execute(text("DELETE FROM homework_results"))
        print("   ✅ Удалены результаты ДЗ")
        
        # Сбрасываем баллы студентов
        await session.execute(text("UPDATE students SET points = 0, level = '🆕 Новичок'"))
        print("   ✅ Сброшены баллы и уровни студентов")
        
        await session.commit()
    
    print("🎯 Создание новых разнообразных результатов...")
    
    # Импортируем функцию создания результатов из init_data
    from scripts.init_data import add_test_homework_results, update_all_student_stats
    
    # Создаем новые результаты
    await add_test_homework_results()
    
    # Обновляем статистику студентов
    await update_all_student_stats()
    
    print("✅ Готово! Теперь у студентов разная статистика")


if __name__ == "__main__":
    asyncio.run(clear_and_recreate_homework_results())
