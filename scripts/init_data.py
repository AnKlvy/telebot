"""
Скрипт для добавления начальных данных в базу данных
"""
import asyncio
import sys
import os

# Добавляем корневую папку проекта в путь
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import (
    init_database, 
    UserRepository, 
    CourseRepository, 
    SubjectRepository
)


async def add_initial_data():
    """Добавить начальные данные"""
    print("🚀 Инициализация базы данных...")
    await init_database()
    
    print("📚 Добавление курсов...")
    # Добавляем курсы
    try:
        course_ent = await CourseRepository.create("ЕНТ")
        course_it = await CourseRepository.create("IT")
        print(f"✅ Курс '{course_ent.name}' создан (ID: {course_ent.id})")
        print(f"✅ Курс '{course_it.name}' создан (ID: {course_it.id})")
    except Exception as e:
        print(f"⚠️ Курсы уже существуют или ошибка: {e}")
        # Получаем существующие курсы
        courses = await CourseRepository.get_all()
        course_ent = next((c for c in courses if c.name == "ЕНТ"), None)
        course_it = next((c for c in courses if c.name == "IT"), None)

    print("📖 Добавление предметов...")
    # Создаем уникальные предметы
    all_subjects = [
        "Математика",
        "Физика",
        "История Казахстана",
        "Химия",
        "Биология",
        "Python",
        "JavaScript",
        "Java"
    ]

    created_subjects = {}
    for subject_name in all_subjects:
        try:
            subject = await SubjectRepository.create(subject_name)
            created_subjects[subject_name] = subject
            print(f"✅ Предмет '{subject.name}' создан (ID: {subject.id})")
        except Exception as e:
            print(f"⚠️ Предмет '{subject_name}' уже существует: {e}")
            # Получаем существующий предмет
            all_existing = await SubjectRepository.get_all()
            existing_subject = next((s for s in all_existing if s.name == subject_name), None)
            if existing_subject:
                created_subjects[subject_name] = existing_subject

    print("🔗 Привязка предметов к курсам...")
    # Привязываем предметы к курсу ЕНТ
    if course_ent:
        ent_subjects = ["Математика", "Физика", "История Казахстана", "Химия", "Биология"]
        for subject_name in ent_subjects:
            if subject_name in created_subjects:
                success = await SubjectRepository.add_to_course(created_subjects[subject_name].id, course_ent.id)
                if success:
                    print(f"✅ Предмет '{subject_name}' привязан к курсу ЕНТ")

    # Привязываем предметы к курсу IT
    if course_it:
        it_subjects = ["Python", "JavaScript", "Java", "Математика"]  # Математика тоже нужна в IT
        for subject_name in it_subjects:
            if subject_name in created_subjects:
                success = await SubjectRepository.add_to_course(created_subjects[subject_name].id, course_it.id)
                if success:
                    print(f"✅ Предмет '{subject_name}' привязан к курсу IT")
    
    print("👥 Добавление тестовых пользователей...")
    # Добавляем тестовых пользователей
    test_users = [
        (123456789, "Админ Тестовый", "admin"),
        (987654321, "Менеджер Тестовый", "manager"),
        (111222333, "Куратор Тестовый", "curator"),
        (444555666, "Преподаватель Тестовый", "teacher"),
        (777888999, "Студент Тестовый", "student"),
    ]
    
    for telegram_id, name, role in test_users:
        try:
            user = await UserRepository.create(telegram_id, name, role)
            print(f"✅ Пользователь '{user.name}' ({user.role}) создан (Telegram ID: {user.telegram_id})")
        except Exception as e:
            print(f"⚠️ Пользователь с Telegram ID {telegram_id} уже существует или ошибка: {e}")
    
    print("🎉 Начальные данные добавлены!")


if __name__ == "__main__":
    asyncio.run(add_initial_data())
