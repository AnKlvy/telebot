"""
Создание уроков и домашних заданий
"""
from database import (
    LessonRepository, HomeworkRepository, QuestionRepository, AnswerOptionRepository
)


async def create_lessons_and_homework(created_subjects):
    """Создание уроков и домашних заданий"""
    try:
        print("📝 Создание уроков и домашних заданий...")
        
        # Данные для уроков и ДЗ по предметам
        lessons_data = {
            "Python": [
                {
                    "name": "Основы Python",
                    "homework": "Основы Python",
                    "questions": [
                        {
                            "text": "Какой тип данных используется для хранения целых чисел в Python?",
                            "microtopic": 1,  # Переменные
                            "answers": [
                                {"text": "int", "is_correct": True},
                                {"text": "float", "is_correct": False},
                                {"text": "str", "is_correct": False},
                                {"text": "bool", "is_correct": False}
                            ]
                        }
                    ]
                },
                {
                    "name": "Циклы и условия",
                    "homework": "Циклы и условия", 
                    "questions": [
                        {
                            "text": "Какой оператор используется для проверки условия в Python?",
                            "microtopic": 3,  # Условия
                            "answers": [
                                {"text": "if", "is_correct": True},
                                {"text": "while", "is_correct": False},
                                {"text": "for", "is_correct": False},
                                {"text": "def", "is_correct": False}
                            ]
                        }
                    ]
                },
                {
                    "name": "Функции",
                    "homework": "Функции",
                    "questions": [
                        {
                            "text": "Какое ключевое слово используется для определения функции в Python?",
                            "microtopic": 5,  # Функции
                            "answers": [
                                {"text": "def", "is_correct": True},
                                {"text": "function", "is_correct": False},
                                {"text": "func", "is_correct": False},
                                {"text": "define", "is_correct": False}
                            ]
                        }
                    ]
                },
                {
                    "name": "ООП в Python",
                    "homework": "ООП в Python",
                    "questions": [
                        {
                            "text": "Какое ключевое слово используется для создания класса в Python?",
                            "microtopic": 6,  # Классы
                            "answers": [
                                {"text": "class", "is_correct": True},
                                {"text": "object", "is_correct": False},
                                {"text": "struct", "is_correct": False},
                                {"text": "type", "is_correct": False}
                            ]
                        }
                    ]
                }
            ],
            "Математика": [
                {
                    "name": "Алгебра",
                    "homework": "Алгебраические выражения",
                    "questions": [
                        {
                            "text": "Чему равно x² - 4x + 4?",
                            "microtopic": 1,  # Алгебра
                            "answers": [
                                {"text": "(x-2)²", "is_correct": True},
                                {"text": "(x+2)²", "is_correct": False},
                                {"text": "(x-4)²", "is_correct": False},
                                {"text": "x²-4", "is_correct": False}
                            ]
                        }
                    ]
                },
                {
                    "name": "Геометрия",
                    "homework": "Площади фигур",
                    "questions": [
                        {
                            "text": "Формула площади круга:",
                            "microtopic": 2,  # Геометрия
                            "answers": [
                                {"text": "πr²", "is_correct": True},
                                {"text": "2πr", "is_correct": False},
                                {"text": "πr", "is_correct": False},
                                {"text": "r²", "is_correct": False}
                            ]
                        }
                    ]
                }
            ],
            "Физика": [
                {
                    "name": "Механика",
                    "homework": "Законы Ньютона",
                    "questions": [
                        {
                            "text": "Первый закон Ньютона также называется:",
                            "microtopic": 1,  # Механика
                            "answers": [
                                {"text": "Закон инерции", "is_correct": True},
                                {"text": "Закон силы", "is_correct": False},
                                {"text": "Закон действия", "is_correct": False},
                                {"text": "Закон движения", "is_correct": False}
                            ]
                        }
                    ]
                }
            ]
        }

        # Создаем уроки и ДЗ
        for subject_name, lessons in lessons_data.items():
            if subject_name not in created_subjects:
                continue
                
            subject = created_subjects[subject_name]
            print(f"   📚 Создание уроков для предмета '{subject_name}'...")
            
            for lesson_data in lessons:
                try:
                    # Создаем урок
                    lesson = await LessonRepository.create(
                        name=lesson_data["name"],
                        subject_id=subject.id
                    )
                    print(f"      ✅ Урок '{lesson.name}' создан (ID: {lesson.id})")
                except ValueError as e:
                    # Урок уже существует, получаем его
                    existing_lessons = await LessonRepository.get_by_subject(subject.id)
                    lesson = next((l for l in existing_lessons if l.name == lesson_data["name"]), None)
                    if lesson:
                        print(f"      ⚠️ Урок '{lesson.name}' уже существует (ID: {lesson.id})")
                    else:
                        print(f"      ❌ Ошибка при создании урока: {e}")
                        continue

                try:
                    # Создаем домашнее задание
                    homework = await HomeworkRepository.create(
                        name=lesson_data["homework"],
                        subject_id=subject.id,
                        lesson_id=lesson.id
                    )
                    print(f"      ✅ ДЗ '{homework.name}' создано (ID: {homework.id})")
                except ValueError as e:
                    print(f"      ⚠️ ДЗ '{lesson_data['homework']}' уже существует")
                
                # Создаем вопросы для ДЗ
                for question_data in lesson_data["questions"]:
                    question = await QuestionRepository.create(
                        homework_id=homework.id,
                        subject_id=subject.id,
                        text=question_data["text"],
                        microtopic_number=question_data["microtopic"],
                        time_limit=30  # 30 секунд на вопрос
                    )
                    print(f"         ✅ Вопрос создан (ID: {question.id})")
                    
                    # Создаем варианты ответов
                    for answer_data in question_data["answers"]:
                        answer = await AnswerOptionRepository.create(
                            question_id=question.id,
                            text=answer_data["text"],
                            is_correct=answer_data["is_correct"]
                        )
                        print(f"            ✅ Вариант ответа создан (ID: {answer.id})")

        # Создаем дополнительные ДЗ для демонстрации
        print("   📝 Создание дополнительных ДЗ...")
        
        additional_homework = [
            {
                "subject": "Python",
                "lesson_name": "Работа с данными",
                "homework_name": "новое дз 2",
                "questions": [
                    {
                        "text": "Какой метод используется для добавления элемента в список?",
                        "microtopic": 2,  # Типы данных
                        "answers": [
                            {"text": "append()", "is_correct": True},
                            {"text": "add()", "is_correct": False},
                            {"text": "insert()", "is_correct": False},
                            {"text": "push()", "is_correct": False}
                        ]
                    },
                    {
                        "text": "Как получить длину списка в Python?",
                        "microtopic": 2,  # Типы данных
                        "answers": [
                            {"text": "len(list)", "is_correct": True},
                            {"text": "list.length", "is_correct": False},
                            {"text": "list.size()", "is_correct": False},
                            {"text": "count(list)", "is_correct": False}
                        ]
                    }
                ]
            }
        ]

        for hw_data in additional_homework:
            subject_name = hw_data["subject"]
            if subject_name not in created_subjects:
                continue
                
            subject = created_subjects[subject_name]
            
            try:
                # Создаем урок
                lesson = await LessonRepository.create(
                    name=hw_data["lesson_name"],
                    subject_id=subject.id
                )
            except ValueError:
                # Урок уже существует, получаем его
                existing_lessons = await LessonRepository.get_by_subject(subject.id)
                lesson = next((l for l in existing_lessons if l.name == hw_data["lesson_name"]), None)
                if not lesson:
                    continue

            try:
                # Создаем ДЗ
                homework = await HomeworkRepository.create(
                    name=hw_data["homework_name"],
                    subject_id=subject.id,
                    lesson_id=lesson.id
                )
                print(f"      ✅ Дополнительное ДЗ '{homework.name}' создано (ID: {homework.id})")
            except ValueError:
                print(f"      ⚠️ ДЗ '{hw_data['homework_name']}' уже существует")
                continue
            
            # Создаем вопросы
            for question_data in hw_data["questions"]:
                question = await QuestionRepository.create(
                    homework_id=homework.id,
                    subject_id=subject.id,
                    text=question_data["text"],
                    microtopic_number=question_data["microtopic"],
                    time_limit=20  # 20 секунд на вопрос
                )
                
                # Создаем варианты ответов
                for answer_data in question_data["answers"]:
                    await AnswerOptionRepository.create(
                        question_id=question.id,
                        text=answer_data["text"],
                        is_correct=answer_data["is_correct"]
                    )

        print(f"📝 Создание уроков и домашних заданий завершено!")

    except Exception as e:
        print(f"❌ Ошибка при создании уроков и ДЗ: {e}")
