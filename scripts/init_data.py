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
    SubjectRepository,
    GroupRepository,
    StudentRepository,
    CuratorRepository,
    TeacherRepository
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
        (955518340, "Андрей Климов", "admin"),
        (7265679697, "Медина Махамбет", "manager"),
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

    print("👥 Добавление тестовых групп...")
    # Тестовые группы для каждого предмета
    test_groups = {
        "Математика": ["МАТ-1", "МАТ-2", "МАТ-3"],
        "Физика": ["ФИЗ-1", "ФИЗ-2"],
        "Python": ["PY-1", "PY-2", "PY-3"],
        "Химия": ["ХИМ-1", "ХИМ-2"],
        "Биология": ["БИО-1", "БИО-2", "БИО-3"],
        "JavaScript": ["JS-1", "JS-2"],
        "Java": ["JAVA-1", "JAVA-2"],
        "История Казахстана": ["ИСТ-1", "ИСТ-2"]
    }

    created_groups_count = 0

    for subject_name, group_names in test_groups.items():
        if subject_name in created_subjects:
            subject = created_subjects[subject_name]
            print(f"📚 Создаем группы для предмета '{subject_name}':")

            for group_name in group_names:
                try:
                    # Проверяем, существует ли уже такая группа
                    existing_groups = await GroupRepository.get_by_subject(subject.id)
                    if any(g.name == group_name for g in existing_groups):
                        print(f"   ⚠️  Группа '{group_name}' уже существует")
                        continue

                    # Создаем группу
                    group = await GroupRepository.create(group_name, subject.id)
                    print(f"   ✅ Создана группа '{group.name}' (ID: {group.id})")
                    created_groups_count += 1

                except Exception as e:
                    print(f"   ❌ Ошибка при создании группы '{group_name}': {e}")

    print(f"📊 Создано групп: {created_groups_count}")

    print("🎓 Добавление тестовых студентов...")
    # Создаем тестовых студентов
    test_students = [
        {
            "name": "Муханбетжан Олжас",
            "telegram_id": 1023397024,
            "group_name": "МАТ-1",
            "subject_name": "Математика",
            "tariff": "premium"
        },
        {
            "name": "Аружан Ахметова",
            "telegram_id": 111111111,
            "group_name": "ХИМ-1",
            "subject_name": "Химия",
            "tariff": "standard"
        },
        {
            "name": "Мадияр Сапаров",
            "telegram_id": 222222222,
            "group_name": "БИО-1",
            "subject_name": "Биология",
            "tariff": "premium"
        },
        {
            "name": "Диана Ержанова",
            "telegram_id": 333333333,
            "group_name": "PY-1",
            "subject_name": "Python",
            "tariff": "standard"
        }
    ]

    created_students_count = 0

    for student_data in test_students:
        try:
            # Находим группу по имени и предмету
            subject = created_subjects.get(student_data["subject_name"])
            if not subject:
                print(f"   ❌ Предмет '{student_data['subject_name']}' не найден для студента {student_data['name']}")
                continue

            groups = await GroupRepository.get_by_subject(subject.id)
            target_group = next((g for g in groups if g.name == student_data["group_name"]), None)

            if not target_group:
                print(f"   ❌ Группа '{student_data['group_name']}' не найдена для студента {student_data['name']}")
                continue

            # Проверяем, существует ли уже пользователь
            existing_user = await UserRepository.get_by_telegram_id(student_data["telegram_id"])
            if existing_user:
                print(f"   ⚠️  Пользователь с Telegram ID {student_data['telegram_id']} уже существует")
                continue

            # Создаем пользователя
            user = await UserRepository.create(
                telegram_id=student_data["telegram_id"],
                name=student_data["name"],
                role='student'
            )

            # Создаем профиль студента
            student = await StudentRepository.create(
                user_id=user.id,
                group_id=target_group.id,
                tariff=student_data["tariff"]
            )

            print(f"   ✅ Создан студент '{student_data['name']}' в группе '{target_group.name}' ({student_data['subject_name']})")
            created_students_count += 1

        except Exception as e:
            print(f"   ❌ Ошибка при создании студента '{student_data['name']}': {e}")

    print(f"📊 Создано студентов: {created_students_count}")

    print("👨‍🏫 Добавление тестовых кураторов...")
    # Создаем тестовых кураторов
    test_curators = [
        {
            "name": "Максат Байкадамов",
            "telegram_id": 1268264380,
            "course_name": "ЕНТ",
            "subject_name": "Математика",
            "group_name": "МАТ-1"
        },
        {
            "name": "Куратор Химии",
            "telegram_id": 444444444,
            "course_name": "ЕНТ",
            "subject_name": "Химия",
            "group_name": "ХИМ-1"
        },
        {
            "name": "Куратор Python",
            "telegram_id": 555555555,
            "course_name": "IT",
            "subject_name": "Python",
            "group_name": "PY-1"
        }
    ]

    created_curators_count = 0

    for curator_data in test_curators:
        try:
            # Находим курс
            course = None
            if curator_data["course_name"] == "ЕНТ":
                course = course_ent
            elif curator_data["course_name"] == "IT":
                course = course_it

            if not course:
                print(f"   ❌ Курс '{curator_data['course_name']}' не найден для куратора {curator_data['name']}")
                continue

            # Находим предмет
            subject = created_subjects.get(curator_data["subject_name"])
            if not subject:
                print(f"   ❌ Предмет '{curator_data['subject_name']}' не найден для куратора {curator_data['name']}")
                continue

            # Находим группу по имени и предмету
            groups = await GroupRepository.get_by_subject(subject.id)
            target_group = next((g for g in groups if g.name == curator_data["group_name"]), None)

            if not target_group:
                print(f"   ❌ Группа '{curator_data['group_name']}' не найдена для куратора {curator_data['name']}")
                continue

            # Проверяем, существует ли уже пользователь
            existing_user = await UserRepository.get_by_telegram_id(curator_data["telegram_id"])
            if existing_user:
                print(f"   ⚠️  Пользователь с Telegram ID {curator_data['telegram_id']} уже существует")
                continue

            # Создаем пользователя
            user = await UserRepository.create(
                telegram_id=curator_data["telegram_id"],
                name=curator_data["name"],
                role='curator'
            )

            # Создаем профиль куратора
            curator = await CuratorRepository.create(
                user_id=user.id,
                course_id=course.id,
                subject_id=subject.id,
                group_id=target_group.id
            )

            print(f"   ✅ Создан куратор '{curator_data['name']}' для группы '{target_group.name}' ({curator_data['subject_name']})")
            created_curators_count += 1

        except Exception as e:
            print(f"   ❌ Ошибка при создании куратора '{curator_data['name']}': {e}")

    print(f"📊 Создано кураторов: {created_curators_count}")

    print("👨‍🏫 Добавление тестовых преподавателей...")
    # Создаем тестовых преподавателей
    test_teachers = [
        {
            "name": "Аслыхан Ещанов",
            "telegram_id": 666666666,  # Заменим на реальный ID если есть
            "course_name": "ЕНТ",
            "subject_name": "Физика",
            "group_name": "ФИЗ-1"
        },
        {
            "name": "Преподаватель Биологии",
            "telegram_id": 777777777,
            "course_name": "ЕНТ",
            "subject_name": "Биология",
            "group_name": "БИО-1"
        },
        {
            "name": "Преподаватель JavaScript",
            "telegram_id": 888888888,
            "course_name": "IT",
            "subject_name": "JavaScript",
            "group_name": "JS-1"
        }
    ]

    created_teachers_count = 0

    for teacher_data in test_teachers:
        try:
            # Находим курс
            course = None
            if teacher_data["course_name"] == "ЕНТ":
                course = course_ent
            elif teacher_data["course_name"] == "IT":
                course = course_it

            if not course:
                print(f"   ❌ Курс '{teacher_data['course_name']}' не найден для преподавателя {teacher_data['name']}")
                continue

            # Находим предмет
            subject = created_subjects.get(teacher_data["subject_name"])
            if not subject:
                print(f"   ❌ Предмет '{teacher_data['subject_name']}' не найден для преподавателя {teacher_data['name']}")
                continue

            # Находим группу по имени и предмету
            groups = await GroupRepository.get_by_subject(subject.id)
            target_group = next((g for g in groups if g.name == teacher_data["group_name"]), None)

            if not target_group:
                print(f"   ❌ Группа '{teacher_data['group_name']}' не найдена для преподавателя {teacher_data['name']}")
                continue

            # Проверяем, существует ли уже пользователь
            existing_user = await UserRepository.get_by_telegram_id(teacher_data["telegram_id"])
            if existing_user:
                print(f"   ⚠️  Пользователь с Telegram ID {teacher_data['telegram_id']} уже существует")
                continue

            # Создаем пользователя
            user = await UserRepository.create(
                telegram_id=teacher_data["telegram_id"],
                name=teacher_data["name"],
                role='teacher'
            )

            # Создаем профиль преподавателя
            teacher = await TeacherRepository.create(
                user_id=user.id,
                course_id=course.id,
                subject_id=subject.id,
                group_id=target_group.id
            )

            print(f"   ✅ Создан преподаватель '{teacher_data['name']}' для группы '{target_group.name}' ({teacher_data['subject_name']})")
            created_teachers_count += 1

        except Exception as e:
            print(f"   ❌ Ошибка при создании преподавателя '{teacher_data['name']}': {e}")

    print(f"📊 Создано преподавателей: {created_teachers_count}")
    print("🎉 Начальные данные добавлены!")


if __name__ == "__main__":
    asyncio.run(add_initial_data())
