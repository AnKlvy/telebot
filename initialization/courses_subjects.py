"""
Создание курсов и предметов
"""
from database import (
    CourseRepository, SubjectRepository, MicrotopicRepository
)


async def create_courses_and_subjects():
    """Создание курсов и предметов"""
    try:
        # Создание курсов
        print("📚 Создание курсов...")

        # Проверяем существующие курсы
        existing_courses = await CourseRepository.get_all()
        course_ent = next((c for c in existing_courses if c.name == "ЕНТ"), None)
        course_it = next((c for c in existing_courses if c.name == "IT"), None)

        if not course_ent:
            course_ent = await CourseRepository.create(name="ЕНТ")
            print(f"   ✅ Курс '{course_ent.name}' создан (ID: {course_ent.id})")
        else:
            print(f"   ⚠️ Курс '{course_ent.name}' уже существует (ID: {course_ent.id})")

        if not course_it:
            course_it = await CourseRepository.create(name="IT")
            print(f"   ✅ Курс '{course_it.name}' создан (ID: {course_it.id})")
        else:
            print(f"   ⚠️ Курс '{course_it.name}' уже существует (ID: {course_it.id})")

        # Создание предметов
        print("📖 Создание предметов...")
        subjects_data = [
            # ЕНТ предметы
            {"name": "Математика", "course": course_ent},
            {"name": "Физика", "course": course_ent},
            {"name": "История Казахстана", "course": course_ent},
            {"name": "Химия", "course": course_ent},
            {"name": "Биология", "course": course_ent},
            # IT предметы
            {"name": "Python", "course": course_it},
            {"name": "JavaScript", "course": course_it},
            {"name": "Java", "course": course_it},
        ]

        # Получаем существующие предметы
        existing_subjects = await SubjectRepository.get_all()
        created_subjects = {}

        for subject_data in subjects_data:
            subject_name = subject_data["name"]
            existing_subject = next((s for s in existing_subjects if s.name == subject_name), None)

            if existing_subject:
                created_subjects[subject_name] = existing_subject
                print(f"   ⚠️ Предмет '{subject_name}' уже существует (ID: {existing_subject.id})")
            else:
                subject = await SubjectRepository.create(name=subject_name)
                created_subjects[subject_name] = subject
                print(f"   ✅ Предмет '{subject_name}' создан (ID: {subject.id})")

        # Привязка предметов к курсам
        print("🔗 Привязка предметов к курсам...")
        
        # ЕНТ предметы
        ent_subjects = ["Математика", "Физика", "История Казахстана", "Химия", "Биология"]
        for subject_name in ent_subjects:
            if subject_name in created_subjects:
                success = await SubjectRepository.add_to_course(created_subjects[subject_name].id, course_ent.id)
                if success:
                    print(f"   ✅ Предмет '{subject_name}' привязан к курсу 'ЕНТ'")
                else:
                    print(f"   ⚠️ Предмет '{subject_name}' уже привязан к курсу 'ЕНТ'")

        # IT предметы (включая математику)
        it_subjects = ["Python", "JavaScript", "Java", "Математика"]
        for subject_name in it_subjects:
            if subject_name in created_subjects:
                success = await SubjectRepository.add_to_course(created_subjects[subject_name].id, course_it.id)
                if success:
                    print(f"   ✅ Предмет '{subject_name}' привязан к курсу 'IT'")
                else:
                    print(f"   ⚠️ Предмет '{subject_name}' уже привязан к курсу 'IT'")

        # Создание микротем для каждого предмета
        print("🔬 Создание микротем...")
        microtopics_data = {
            "Математика": [
                "Алгебра", "Геометрия", "Тригонометрия", "Логарифмы", "Производные",
                "Интегралы", "Комбинаторика", "Вероятность", "Статистика", "Функции"
            ],
            "Физика": [
                "Механика", "Термодинамика", "Электричество", "Магнетизм", "Оптика",
                "Атомная физика", "Колебания", "Волны", "Кинематика", "Динамика"
            ],
            "История Казахстана": [
                "Древний Казахстан", "Средневековье", "Казахское ханство", "Колониальный период", "Советский период",
                "Независимость", "Культура", "Экономика", "Политика", "Современность"
            ],
            "Химия": [
                "Атомы", "Молекулы", "Периодическая система", "Химические связи", "Реакции",
                "Кислоты", "Основания", "Соли", "Органическая химия", "Неорганическая химия"
            ],
            "Биология": [
                "Клетка", "Генетика", "Эволюция", "Экология", "Анатомия",
                "Физиология", "Ботаника", "Зоология", "Микробиология", "Биохимия"
            ],
            "Python": [
                "Переменные", "Типы данных", "Условия", "Циклы", "Функции",
                "Классы", "Модули", "Исключения", "Файлы", "Библиотеки"
            ],
            "JavaScript": [
                "Переменные", "Функции", "Объекты", "Массивы", "DOM",
                "События", "Асинхронность", "Промисы", "Fetch", "ES6+"
            ],
            "Java": [
                "Переменные", "Классы", "Наследование", "Интерфейсы", "Коллекции",
                "Исключения", "Потоки", "Generics", "Аннотации", "Lambda"
            ]
        }

        for subject_name, topics in microtopics_data.items():
            if subject_name in created_subjects:
                subject = created_subjects[subject_name]
                for topic_name in topics:
                    try:
                        microtopic = await MicrotopicRepository.create(
                            name=topic_name,
                            subject_id=subject.id
                        )
                        print(f"   ✅ Микротема '{topic_name}' создана для предмета '{subject_name}' (номер: {microtopic.number})")
                    except ValueError as e:
                        print(f"   ⚠️ Микротема '{topic_name}' уже существует для предмета '{subject_name}'")

        print(f"📚 Создание курсов и предметов завершено!")
        return created_subjects, course_ent, course_it

    except Exception as e:
        print(f"❌ Ошибка при создании курсов и предметов: {e}")
        return {}, None, None
