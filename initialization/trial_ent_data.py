"""
Инициализация данных для пробного ЕНТ
"""
import asyncio
import logging
import sys
import os

# Добавляем корневую папку проекта в путь
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import (
    SubjectRepository, HomeworkRepository, QuestionRepository,
    AnswerOptionRepository, LessonRepository, MicrotopicRepository
)

logger = logging.getLogger(__name__)


async def create_trial_ent_questions():
    """Создать вопросы для предметов пробного ЕНТ"""
    
    # Предметы, которые нужны для пробного ЕНТ с минимальным количеством вопросов
    trial_ent_subjects = {
        "История Казахстана": 25,      # Нужно минимум 20
        "Математическая грамотность": 15,  # Нужно минимум 10
        "Математика": 60,              # Нужно минимум 50
        "География": 60,               # Нужно минимум 50
        "Биология": 60,                # Нужно минимум 50
        "Химия": 60,                   # Нужно минимум 50
        "Информатика": 60,             # Нужно минимум 50
        "Всемирная история": 60        # Нужно минимум 50
    }
    
    subjects = await SubjectRepository.get_all()
    subject_map = {s.name: s for s in subjects}
    
    for subject_name, question_count in trial_ent_subjects.items():
        if subject_name in subject_map:
            subject = subject_map[subject_name]
            print(f"   📝 Создаем вопросы для {subject_name}...")
            
            try:
                await create_questions_for_subject(subject.id, subject_name, question_count)
                print(f"   ✅ Создано {question_count} вопросов для {subject_name}")
            except Exception as e:
                print(f"   ❌ Ошибка при создании вопросов для {subject_name}: {e}")
        else:
            print(f"   ⚠️ Предмет '{subject_name}' не найден в базе данных")


async def create_questions_for_subject(subject_id: int, subject_name: str, question_count: int):
    """Создать вопросы для конкретного предмета"""
    
    # Получаем или создаем урок
    lessons = await LessonRepository.get_by_subject(subject_id)
    if not lessons:
        # Создаем тестовый урок
        lesson = await LessonRepository.create(
            name=f"Урок 1 - {subject_name}",
            subject_id=subject_id,
            course_id=1  # Курс ЕНТ
        )
    else:
        lesson = lessons[0]
    
    # Получаем или создаем домашнее задание
    homeworks = await HomeworkRepository.get_by_lesson(lesson.id)
    if not homeworks:
        # Создаем тестовое домашнее задание
        homework = await HomeworkRepository.create(
            name=f"ДЗ 1 - {subject_name}",
            subject_id=subject_id,
            lesson_id=lesson.id
        )
    else:
        homework = homeworks[0]
    
    # Получаем или создаем микротемы для предмета
    microtopics = await MicrotopicRepository.get_by_subject(subject_id)
    if not microtopics:
        # Создаем базовые микротемы
        microtopic_names = [
            "Основы",
            "Базовые понятия", 
            "Практические задачи",
            "Теория",
            "Применение"
        ]
        
        for name in microtopic_names:
            try:
                await MicrotopicRepository.create(
                    name=name,
                    subject_id=subject_id
                )
            except Exception as e:
                # Микротема уже может существовать, проверим конкретную ошибку
                if "уже существует" not in str(e):
                    print(f"      ⚠️ Ошибка при создании микротемы {name}: {e}")
                pass
        
        # Обновляем список микротем
        microtopics = await MicrotopicRepository.get_by_subject(subject_id)
    
    microtopic_numbers = [mt.number for mt in microtopics[:5]]  # Берем первые 5
    if not microtopic_numbers:
        microtopic_numbers = [1]  # Fallback
    
    # Проверяем, сколько вопросов уже есть
    existing_questions = await QuestionRepository.get_by_homework(homework.id)
    if len(existing_questions) >= question_count:
        return  # Уже достаточно вопросов
    
    # Создаем недостающие вопросы
    questions_to_create = question_count - len(existing_questions)
    
    for i in range(questions_to_create):
        question_num = len(existing_questions) + i + 1
        microtopic_num = microtopic_numbers[i % len(microtopic_numbers)]

        # Варьируем время ответа для разнообразия (30-90 секунд)
        time_limits = [30, 45, 60, 75, 90]
        time_limit = time_limits[i % len(time_limits)]

        # Создаем вопрос
        question = await QuestionRepository.create(
            homework_id=homework.id,
            text=f"Тестовый вопрос {question_num} по предмету {subject_name}",
            subject_id=subject_id,
            microtopic_number=microtopic_num,
            time_limit=time_limit
        )
        
        # Создаем варианты ответов
        options = [
            ("Правильный ответ", True),
            ("Неправильный ответ 1", False),
            ("Неправильный ответ 2", False),
            ("Неправильный ответ 3", False)
        ]
        
        for text, is_correct in options:
            await AnswerOptionRepository.create(
                question_id=question.id,
                text=text,
                is_correct=is_correct
            )


async def create_missing_subjects():
    """Создать недостающие предметы для пробного ЕНТ"""
    
    required_subjects = [
        "История Казахстана",
        "Математическая грамотность",
        "География", 
        "Информатика",
        "Всемирная история"
    ]
    
    existing_subjects = await SubjectRepository.get_all()
    existing_names = {s.name for s in existing_subjects}
    
    for subject_name in required_subjects:
        if subject_name not in existing_names:
            try:
                subject = await SubjectRepository.create(subject_name)
                print(f"   ✅ Создан предмет: {subject.name}")
            except Exception as e:
                print(f"   ⚠️ Предмет {subject_name} уже существует или ошибка: {e}")


async def fix_broken_questions():
    """Исправить вопросы без вариантов ответов"""
    print("   🔧 Исправление проблемных вопросов...")

    subjects = await SubjectRepository.get_all()
    fixed_count = 0

    for subject in subjects:
        questions = await QuestionRepository.get_by_subject(subject.id)

        for question in questions:
            # Проверяем варианты ответов
            options = await AnswerOptionRepository.get_by_question(question.id)

            if not options:
                # Создаем варианты ответов
                answer_options = [
                    ('Правильный ответ', True),
                    ('Неправильный ответ 1', False),
                    ('Неправильный ответ 2', False),
                    ('Неправильный ответ 3', False)
                ]

                for text, is_correct in answer_options:
                    await AnswerOptionRepository.create(
                        question_id=question.id,
                        text=text,
                        is_correct=is_correct
                    )

                fixed_count += 1

    if fixed_count > 0:
        print(f"   ✅ Исправлено {fixed_count} вопросов")


async def update_question_times():
    """Обновить время ответа для разнообразия"""
    print("   ⏰ Обновление времени ответа...")

    subjects = await SubjectRepository.get_all()
    time_limits = [30, 45, 60, 75, 90]
    updated_count = 0

    for subject in subjects:
        questions = await QuestionRepository.get_by_subject(subject.id)

        for i, question in enumerate(questions):
            new_time_limit = time_limits[i % len(time_limits)]

            if question.time_limit != new_time_limit:
                await QuestionRepository.update(question.id, time_limit=new_time_limit)
                updated_count += 1

    if updated_count > 0:
        print(f"   ✅ Обновлено время для {updated_count} вопросов")


async def init_trial_ent_data():
    """Главная функция инициализации данных пробного ЕНТ"""
    print("🎯 Инициализация данных пробного ЕНТ...")

    # Создаем недостающие предметы
    print("   📚 Создание недостающих предметов...")
    await create_missing_subjects()

    # Создаем вопросы для всех предметов
    print("   📝 Создание вопросов для пробного ЕНТ...")
    await create_trial_ent_questions()

    # Исправляем проблемные вопросы
    await fix_broken_questions()

    # Обновляем время ответа
    await update_question_times()

    print("   ✅ Инициализация данных пробного ЕНТ завершена")


if __name__ == "__main__":
    # Для тестирования модуля отдельно
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from database.database import init_database
    
    async def test():
        await init_database()
        await init_trial_ent_data()
    
    asyncio.run(test())
