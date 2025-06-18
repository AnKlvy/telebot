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
    TeacherRepository,
    ManagerRepository,
    MicrotopicRepository,
    LessonRepository,
    HomeworkRepository,
    QuestionRepository,
    AnswerOptionRepository,
    MonthTestRepository,
    MonthTestMicrotopicRepository,
    BonusTestRepository,
    BonusQuestionRepository,
    BonusAnswerOptionRepository,
    HomeworkResultRepository,
    QuestionResultRepository,
    get_db_session
)
from database.models import Microtopic, Subject
from sqlalchemy import text, select
from sqlalchemy.exc import IntegrityError


async def migrate_microtopics():
    """Миграция микротем: добавление поля number и автоматическая нумерация"""
    print("🔄 Проверяем необходимость миграции микротем...")

    # Проверяем, есть ли уже поле number
    async with get_db_session() as session:
        try:
            await session.execute(text("SELECT number FROM microtopics LIMIT 1"))
            print("✅ Поле 'number' уже существует в таблице microtopics")
            return  # Миграция уже выполнена
        except Exception:
            print("📝 Поле 'number' не найдено, начинаем миграцию...")

    # Добавляем поле number в отдельной транзакции
    async with get_db_session() as session:
        try:
            print("📝 Добавляем поле 'number' в таблицу microtopics...")
            await session.execute(text("ALTER TABLE microtopics ADD COLUMN number INTEGER"))
            await session.commit()
            print("✅ Поле 'number' добавлено")
        except Exception as e:
            print(f"⚠️ Ошибка при добавлении поля 'number': {e}")
            await session.rollback()
            return

    # Выполняем нумерацию в отдельной транзакции
    async with get_db_session() as session:
        try:
            # 3. Получаем все предметы
            subjects_result = await session.execute(select(Subject))
            subjects = subjects_result.scalars().all()

            print(f"📊 Найдено предметов для миграции: {len(subjects)}")

            # 4. Для каждого предмета нумеруем микротемы и обрабатываем дубликаты
            for subject in subjects:
                print(f"🔢 Обрабатываем предмет: {subject.name}")

                # Получаем микротемы предмета, отсортированные по ID (порядок создания)
                microtopics_result = await session.execute(
                    select(Microtopic)
                    .where(Microtopic.subject_id == subject.id)
                    .order_by(Microtopic.id)
                )
                microtopics = microtopics_result.scalars().all()

                # Обрабатываем дубликаты названий
                seen_names = {}
                renamed_count = 0

                for microtopic in microtopics:
                    original_name = microtopic.name

                    # Если название уже встречалось, добавляем номер
                    if original_name in seen_names:
                        seen_names[original_name] += 1
                        new_name = f"{original_name} ({seen_names[original_name]})"
                        microtopic.name = new_name
                        renamed_count += 1
                        print(f"  🔄 Переименована: '{original_name}' → '{new_name}'")
                    else:
                        seen_names[original_name] = 1

                # Присваиваем номера
                for i, microtopic in enumerate(microtopics, 1):
                    if microtopic.number is None:  # Только если номер еще не присвоен
                        microtopic.number = i
                        print(f"  📌 Микротема '{microtopic.name}' → номер {i}")

                await session.commit()

                if renamed_count > 0:
                    print(f"🔄 Переименовано дубликатов: {renamed_count}")
                print(f"✅ Обработано микротем для предмета '{subject.name}': {len(microtopics)}")

            print("🎉 Нумерация микротем завершена успешно!")

        except Exception as e:
            print(f"❌ Ошибка при нумерации микротем: {e}")
            await session.rollback()
            raise

    # Обновляем ограничения в отдельной транзакции
    async with get_db_session() as session:
        try:
            # 5. Удаляем старое ограничение уникальности (если существует)
            try:
                await session.execute(text("ALTER TABLE microtopics DROP CONSTRAINT unique_microtopic_per_subject"))
                await session.commit()
                print("🗑️ Удалено старое ограничение уникальности")
            except Exception:
                print("ℹ️ Старое ограничение уникальности не найдено")

            # 6. Добавляем новое ограничение уникальности по номеру
            try:
                await session.execute(text(
                    "ALTER TABLE microtopics ADD CONSTRAINT unique_microtopic_number_per_subject "
                    "UNIQUE (number, subject_id)"
                ))
                await session.commit()
                print("✅ Добавлено новое ограничение уникальности по номеру")
            except IntegrityError:
                print("ℹ️ Ограничение уникальности по номеру уже существует")

            # 7. Добавляем ограничение уникальности по названию
            try:
                await session.execute(text(
                    "ALTER TABLE microtopics ADD CONSTRAINT unique_microtopic_name_per_subject "
                    "UNIQUE (name, subject_id)"
                ))
                await session.commit()
                print("✅ Добавлено ограничение уникальности по названию")
            except IntegrityError:
                print("ℹ️ Ограничение уникальности по названию уже существует")

            # 8. Делаем поле number обязательным
            try:
                await session.execute(text("ALTER TABLE microtopics ALTER COLUMN number SET NOT NULL"))
                await session.commit()
                print("✅ Поле 'number' сделано обязательным")
            except Exception as e:
                print(f"⚠️ Не удалось сделать поле 'number' обязательным: {e}")

            print("🎉 Миграция микротем завершена успешно!")

        except Exception as e:
            print(f"❌ Ошибка при обновлении ограничений: {e}")
            await session.rollback()
            raise


async def add_initial_data():
    """Добавить начальные данные"""
    print("🚀 Инициализация базы данных...")
    await init_database()

    # Выполняем миграцию микротем
    await migrate_microtopics()
    
    print("📚 Добавление курсов...")
    # Получаем существующие курсы
    existing_courses = await CourseRepository.get_all()
    existing_course_names = {course.name: course for course in existing_courses}

    # Проверяем и создаем курс ЕНТ
    if "ЕНТ" in existing_course_names:
        course_ent = existing_course_names["ЕНТ"]
        print(f"⚠️ Курс 'ЕНТ' уже существует (ID: {course_ent.id})")
    else:
        try:
            course_ent = await CourseRepository.create("ЕНТ")
            print(f"✅ Курс '{course_ent.name}' создан (ID: {course_ent.id})")
        except Exception as e:
            print(f"❌ Ошибка при создании курса 'ЕНТ': {e}")
            course_ent = None

    # Проверяем и создаем курс IT
    if "IT" in existing_course_names:
        course_it = existing_course_names["IT"]
        print(f"⚠️ Курс 'IT' уже существует (ID: {course_it.id})")
    else:
        try:
            course_it = await CourseRepository.create("IT")
            print(f"✅ Курс '{course_it.name}' создан (ID: {course_it.id})")
        except Exception as e:
            print(f"❌ Ошибка при создании курса 'IT': {e}")
            course_it = None

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

    # Получаем существующие предметы
    existing_subjects = await SubjectRepository.get_all()
    existing_subject_names = {subject.name: subject for subject in existing_subjects}

    created_subjects = {}
    for subject_name in all_subjects:
        if subject_name in existing_subject_names:
            created_subjects[subject_name] = existing_subject_names[subject_name]
            print(f"⚠️ Предмет '{subject_name}' уже существует (ID: {existing_subject_names[subject_name].id})")
        else:
            try:
                subject = await SubjectRepository.create(subject_name)
                created_subjects[subject_name] = subject
                print(f"✅ Предмет '{subject.name}' создан (ID: {subject.id})")
            except Exception as e:
                print(f"❌ Ошибка при создании предмета '{subject_name}': {e}")

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
        (5205775566, "Мадияр Сапаров", "admin"),
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
            "name": "Айсулу Нурбекова",
            "telegram_id": 333444555,
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
        },
        # Дополнительные студенты для математики
        {
            "name": "Алия Нурланова",
            "telegram_id": 444444445,
            "group_name": "МАТ-2",
            "subject_name": "Математика",
            "tariff": "premium"
        },
        {
            "name": "Ерлан Касымов",
            "telegram_id": 555555556,
            "group_name": "МАТ-3",
            "subject_name": "Математика",
            "tariff": "standard"
        },
        # Дополнительные студенты для химии
        {
            "name": "Жанара Омарова",
            "telegram_id": 666666667,
            "group_name": "ХИМ-2",
            "subject_name": "Химия",
            "tariff": "premium"
        },
        {
            "name": "Данияр Абдуллаев",
            "telegram_id": 777777778,
            "group_name": "ХИМ-1",
            "subject_name": "Химия",
            "tariff": "standard"
        },
        # Дополнительные студенты для биологии
        {
            "name": "Айгерим Токтарова",
            "telegram_id": 888888889,
            "group_name": "БИО-2",
            "subject_name": "Биология",
            "tariff": "premium"
        },
        {
            "name": "Нурлан Жумабеков",
            "telegram_id": 999999990,
            "group_name": "БИО-3",
            "subject_name": "Биология",
            "tariff": "standard"
        },
        # Дополнительные студенты для физики
        {
            "name": "Асель Мухамедова",
            "telegram_id": 101010101,
            "group_name": "ФИЗ-1",
            "subject_name": "Физика",
            "tariff": "premium"
        },
        {
            "name": "Бауыржан Сейтов",
            "telegram_id": 121212121,
            "group_name": "ФИЗ-2",
            "subject_name": "Физика",
            "tariff": "standard"
        },
        # Дополнительные студенты для Python
        {
            "name": "Камила Рахимова",
            "telegram_id": 131313131,
            "group_name": "PY-2",
            "subject_name": "Python",
            "tariff": "premium"
        },
        {
            "name": "Арман Досжанов",
            "telegram_id": 141414141,
            "group_name": "PY-3",
            "subject_name": "Python",
            "tariff": "standard"
        },
        # Дополнительные студенты для JavaScript
        {
            "name": "Сабина Калиева",
            "telegram_id": 151515151,
            "group_name": "JS-1",
            "subject_name": "JavaScript",
            "tariff": "premium"
        },
        {
            "name": "Темирлан Ахметов",
            "telegram_id": 161616161,
            "group_name": "JS-2",
            "subject_name": "JavaScript",
            "tariff": "standard"
        },
        # Дополнительные студенты для Java
        {
            "name": "Айжан Бекмуратова",
            "telegram_id": 171717171,
            "group_name": "JAVA-1",
            "subject_name": "Java",
            "tariff": "premium"
        },
        {
            "name": "Ерболат Нуржанов",
            "telegram_id": 181818181,
            "group_name": "JAVA-2",
            "subject_name": "Java",
            "tariff": "standard"
        },
        # Дополнительные студенты для истории Казахстана
        {
            "name": "Гульнара Сарсенова",
            "telegram_id": 191919191,
            "group_name": "ИСТ-1",
            "subject_name": "История Казахстана",
            "tariff": "premium"
        },
        {
            "name": "Максат Ержанов",
            "telegram_id": 202020202,
            "group_name": "ИСТ-2",
            "subject_name": "История Казахстана",
            "tariff": "standard"
        },
        # Андрей Климов - основной разработчик/тестировщик
        {
            "name": "Андрей Климов",
            "telegram_id": 955518340,
            "group_name": "PY-1",  # Python группа для разработчика
            "subject_name": "Python",
            "tariff": "premium"
        },
        # Медина Махамбет - тестирование как студент
        {
            "name": "Медина Махамбет",
            "telegram_id": 7265679697,
            "group_name": "МАТ-1",  # Математика группа
            "subject_name": "Математика",
            "tariff": "premium"
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
                # Проверяем, есть ли у него профиль студента
                existing_student = await StudentRepository.get_by_user_id(existing_user.id)
                if existing_student:
                    print(f"   ⚠️  Профиль студента уже существует для пользователя {existing_user.name}")
                    continue
                else:
                    user = existing_user
                    print(f"   🔄 Создаем профиль студента для существующего пользователя {user.name}")
            else:
                # Создаем пользователя
                user = await UserRepository.create(
                    telegram_id=student_data["telegram_id"],
                    name=student_data["name"],
                    role='student'
                )
                print(f"   ✅ Создан пользователь: {user.name}")

            # Создаем профиль студента
            student = await StudentRepository.create(
                user_id=user.id,
                tariff=student_data["tariff"]
            )

            # Привязываем студента к группе
            await StudentRepository.set_groups(student.id, [target_group.id])

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
                # Проверяем, есть ли у него профиль куратора
                existing_curator = await CuratorRepository.get_by_user_id(existing_user.id)
                if existing_curator:
                    print(f"   ⚠️  Профиль куратора уже существует для пользователя {existing_user.name}")
                    continue
                else:
                    user = existing_user
                    print(f"   🔄 Создаем профиль куратора для существующего пользователя {user.name}")
            else:
                # Создаем пользователя
                user = await UserRepository.create(
                    telegram_id=curator_data["telegram_id"],
                    name=curator_data["name"],
                    role='curator'
                )
                print(f"   ✅ Создан пользователь: {user.name}")

            # Создаем профиль куратора
            curator = await CuratorRepository.create(
                user_id=user.id,
                course_id=course.id,
                subject_id=subject.id
            )

            # Добавляем куратора в группу через M2M связь
            success = await CuratorRepository.add_curator_to_group(curator.id, target_group.id)
            if success:
                print(f"   ✅ Создан куратор '{curator_data['name']}' для группы '{target_group.name}' ({curator_data['subject_name']})")
            else:
                print(f"   ⚠️ Куратор '{curator_data['name']}' создан, но не удалось привязать к группе '{target_group.name}'")

            created_curators_count += 1

        except Exception as e:
            print(f"   ❌ Ошибка при создании куратора '{curator_data['name']}': {e}")

    print(f"📊 Создано кураторов: {created_curators_count}")

    # Добавляем дополнительные группы для демонстрации Many-to-Many связи
    print("🔗 Добавление дополнительных групп для кураторов...")
    try:
        # Максат Байкадамов - добавляем МАТ-2 и МАТ-3
        curators = await CuratorRepository.get_all()
        math_curator = next((c for c in curators if c.user.telegram_id == 1268264380), None)
        if math_curator:
            math_subject = created_subjects.get("Математика")
            if math_subject:
                groups = await GroupRepository.get_by_subject(math_subject.id)
                for group_name in ["МАТ-2", "МАТ-3"]:
                    group = next((g for g in groups if g.name == group_name), None)
                    if group:
                        await CuratorRepository.add_curator_to_group(math_curator.id, group.id)
                        print(f"   ✅ {math_curator.user.name} -> {group_name}")

        # Куратор Химии - добавляем ХИМ-2
        chem_curator = next((c for c in curators if c.user.telegram_id == 444444444), None)
        if chem_curator:
            chem_subject = created_subjects.get("Химия")
            if chem_subject:
                groups = await GroupRepository.get_by_subject(chem_subject.id)
                group = next((g for g in groups if g.name == "ХИМ-2"), None)
                if group:
                    await CuratorRepository.add_curator_to_group(chem_curator.id, group.id)
                    print(f"   ✅ {chem_curator.user.name} -> ХИМ-2")

        # Куратор Python - добавляем PY-2 и PY-3
        py_curator = next((c for c in curators if c.user.telegram_id == 555555555), None)
        if py_curator:
            py_subject = created_subjects.get("Python")
            if py_subject:
                groups = await GroupRepository.get_by_subject(py_subject.id)
                for group_name in ["PY-2", "PY-3"]:
                    group = next((g for g in groups if g.name == group_name), None)
                    if group:
                        await CuratorRepository.add_curator_to_group(py_curator.id, group.id)
                        print(f"   ✅ {py_curator.user.name} -> {group_name}")

    except Exception as e:
        print(f"   ⚠️ Ошибка: {e}")

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
                subject_id=subject.id
            )

            # Добавляем преподавателя в группу через M2M связь
            success = await TeacherRepository.add_teacher_to_group(teacher.id, target_group.id)
            if not success:
                print(f"   ⚠️ Преподаватель '{teacher_data['name']}' создан, но не удалось привязать к группе '{target_group.name}'")

            print(f"   ✅ Создан преподаватель '{teacher_data['name']}' для группы '{target_group.name}' ({teacher_data['subject_name']})")
            created_teachers_count += 1

        except Exception as e:
            print(f"   ❌ Ошибка при создании преподавателя '{teacher_data['name']}': {e}")

    print(f"📊 Создано преподавателей: {created_teachers_count}")

    print("👨‍💼 Добавление тестовых менеджеров...")
    # Создаем тестовых менеджеров
    test_managers = [
        {
            "name": "Медина Махамбет",
            "telegram_id": 7265679697  # Реальный пользователь
        },
        {
            "name": "Менеджер Тестовый",
            "telegram_id": 999999999
        }
    ]

    created_managers_count = 0

    for manager_data in test_managers:
        try:
            # Проверяем, существует ли уже пользователь
            existing_user = await UserRepository.get_by_telegram_id(manager_data["telegram_id"])
            if existing_user:
                print(f"   ⚠️  Пользователь с Telegram ID {manager_data['telegram_id']} уже существует")
                continue

            # Создаем пользователя
            user = await UserRepository.create(
                telegram_id=manager_data["telegram_id"],
                name=manager_data["name"],
                role='manager'
            )

            # Создаем профиль менеджера
            manager = await ManagerRepository.create(user_id=user.id)

            print(f"   ✅ Создан менеджер '{manager_data['name']}'")
            created_managers_count += 1

        except Exception as e:
            print(f"   ❌ Ошибка при создании менеджера '{manager_data['name']}': {e}")

    print(f"📊 Создано менеджеров: {created_managers_count}")

    print("👑 Добавление ролей для админов...")
    # Добавляем всем админам все роли с соответствующими данными
    await add_admin_roles(created_subjects, course_ent, course_it)

    print("📝 Добавление тестовых микротем...")
    # Создаем тестовые микротемы
    test_microtopics = {
        "Математика": ["Дроби", "Проценты", "Уравнения", "Геометрия"],
        "Физика": ["Механика", "Оптика", "Термодинамика", "Электричество"],
        "Химия": ["Органическая химия", "Неорганическая химия", "Реакции"],
        "Биология": ["Клетка", "Генетика", "Эволюция", "Экология"],
        "Python": ["Переменные", "Функции", "Классы", "Модули"],
        "JavaScript": ["DOM", "События", "Асинхронность", "Промисы"],
        "Java": ["ООП", "Коллекции", "Исключения", "Потоки"]
    }

    # Получаем существующие микротемы для проверки дублей
    existing_microtopics = await MicrotopicRepository.get_all()
    existing_by_subject = {}
    for mt in existing_microtopics:
        if mt.subject_id not in existing_by_subject:
            existing_by_subject[mt.subject_id] = set()
        existing_by_subject[mt.subject_id].add(mt.name)

    created_microtopics_count = 0

    for subject_name, microtopic_names in test_microtopics.items():
        if subject_name in created_subjects:
            subject = created_subjects[subject_name]
            existing_names = existing_by_subject.get(subject.id, set())

            print(f"📝 Создаем микротемы для предмета '{subject_name}':")

            for microtopic_name in microtopic_names:
                if microtopic_name in existing_names:
                    print(f"   ⚠️  Микротема '{microtopic_name}' уже существует")
                    continue

                try:
                    microtopic = await MicrotopicRepository.create(microtopic_name, subject.id)
                    print(f"   ✅ Создана микротема '{microtopic.name}' (ID: {microtopic.id})")
                    created_microtopics_count += 1

                except Exception as e:
                    print(f"   ❌ Ошибка при создании микротемы '{microtopic_name}': {e}")

    print(f"📊 Создано микротем: {created_microtopics_count}")

    print("📚 Добавление тестовых уроков...")
    # Создаем тестовые уроки
    test_lessons = {
        "Математика": ["Урок 1: Основы алгебры", "Урок 2: Линейные уравнения", "Урок 3: Квадратные уравнения", "Урок 4: Системы уравнений"],
        "Физика": ["Урок 1: Кинематика", "Урок 2: Динамика", "Урок 3: Законы Ньютона", "Урок 4: Работа и энергия"],
        "Химия": ["Урок 1: Атомная структура", "Урок 2: Химические связи", "Урок 3: Реакции окисления", "Урок 4: Органические соединения"],
        "Биология": ["Урок 1: Строение клетки", "Урок 2: Митоз и мейоз", "Урок 3: Законы Менделя", "Урок 4: Естественный отбор"],
        "История Казахстана": ["Урок 1: Древний Казахстан", "Урок 2: Средневековье", "Урок 3: Казахское ханство", "Урок 4: Современность"],
        "Python": ["Урок 1: Синтаксис Python", "Урок 2: Работа с данными", "Урок 3: Функции и модули", "Урок 4: ООП в Python"],
        "JavaScript": ["Урок 1: Основы JS", "Урок 2: Работа с DOM", "Урок 3: Асинхронный JS", "Урок 4: Современный JS"],
        "Java": ["Урок 1: Основы Java", "Урок 2: ООП в Java", "Урок 3: Коллекции", "Урок 4: Многопоточность"]
    }

    # Получаем существующие уроки для проверки дублей
    existing_lessons = await LessonRepository.get_all()
    existing_lessons_by_subject = {}
    for lesson in existing_lessons:
        if lesson.subject_id not in existing_lessons_by_subject:
            existing_lessons_by_subject[lesson.subject_id] = set()
        existing_lessons_by_subject[lesson.subject_id].add(lesson.name)

    created_lessons_count = 0

    for subject_name, lesson_names in test_lessons.items():
        if subject_name in created_subjects:
            subject = created_subjects[subject_name]
            existing_names = existing_lessons_by_subject.get(subject.id, set())

            print(f"📚 Создаем уроки для предмета '{subject_name}':")

            for lesson_name in lesson_names:
                if lesson_name in existing_names:
                    print(f"   ⚠️  Урок '{lesson_name}' уже существует")
                    continue

                try:
                    lesson = await LessonRepository.create(lesson_name, subject.id)
                    print(f"   ✅ Создан урок '{lesson.name}' (ID: {lesson.id})")
                    created_lessons_count += 1

                except Exception as e:
                    print(f"   ❌ Ошибка при создании урока '{lesson_name}': {e}")

    print(f"📊 Создано уроков: {created_lessons_count}")

    print("📝 Добавление тестовых домашних заданий...")
    # Создаем тестовые домашние задания
    await add_test_homework_data(created_subjects, course_ent, course_it)

    print("🧪 Добавление тестовых бонусных тестов...")
    # Создаем тестовые бонусные тесты
    await add_test_bonus_tests()

    print("📅 Добавление тестовых тестов месяца...")
    # Создаем тестовые тесты месяца
    await add_test_month_tests(created_subjects, course_ent, course_it)

    print("📊 Добавление тестовых результатов ДЗ...")
    # Создаем тестовые результаты для демонстрации статистики
    await add_test_homework_results()

    print("🔄 Обновление баллов и уровней студентов...")
    # Обновляем баллы и уровни всех студентов
    await update_all_student_stats()

    print("🔗 Привязка студентов к курсам...")
    # Привязываем студентов к курсам на основе их предметов
    await assign_students_to_courses(created_subjects, course_ent, course_it)

    print("🎉 Начальные данные добавлены!")


async def add_test_homework_data(created_subjects, course_ent, course_it):
    """Добавление тестовых данных для домашних заданий"""
    try:
        # Получаем менеджера для создания ДЗ
        managers = await ManagerRepository.get_all()
        if not managers:
            print("   ❌ Не найден менеджер для создания ДЗ")
            return

        manager_user = managers[0].user  # Берем первого менеджера

        # Получаем уроки для создания ДЗ
        lessons = await LessonRepository.get_all()
        if not lessons:
            print("   ❌ Не найдены уроки для создания ДЗ")
            return

        # Создаем ДЗ для разных предметов
        homework_data = [
            # Химия - 4 ДЗ
            {
                "name": "Базовое ДЗ по алканам",
                "subject_name": "Химия",
                "course": course_ent,
                "questions": [
                    {
                        "text": "Какая общая формула алканов?",
                        "time_limit": 30,
                        "microtopic_number": 1,
                        "answers": [
                            {"text": "CnH2n+2", "is_correct": True},
                            {"text": "CnH2n", "is_correct": False},
                            {"text": "CnH2n-2", "is_correct": False},
                            {"text": "CnHn", "is_correct": False}
                        ]
                    }
                ]
            },
            {
                "name": "Алкены и алкины",
                "subject_name": "Химия",
                "course": course_ent,
                "questions": [
                    {
                        "text": "Какая общая формула алкенов?",
                        "time_limit": 30,
                        "microtopic_number": 2,
                        "answers": [
                            {"text": "CnH2n", "is_correct": True},
                            {"text": "CnH2n+2", "is_correct": False},
                            {"text": "CnH2n-2", "is_correct": False},
                            {"text": "CnHn", "is_correct": False}
                        ]
                    }
                ]
            },
            {
                "name": "Ароматические соединения",
                "subject_name": "Химия",
                "course": course_ent,
                "questions": [
                    {
                        "text": "Какое соединение является простейшим ароматическим?",
                        "time_limit": 30,
                        "microtopic_number": 3,
                        "answers": [
                            {"text": "Бензол", "is_correct": True},
                            {"text": "Толуол", "is_correct": False},
                            {"text": "Фенол", "is_correct": False},
                            {"text": "Анилин", "is_correct": False}
                        ]
                    }
                ]
            },
            {
                "name": "Кислоты и основания",
                "subject_name": "Химия",
                "course": course_ent,
                "questions": [
                    {
                        "text": "Что показывает pH раствора?",
                        "time_limit": 30,
                        "microtopic_number": 4,
                        "answers": [
                            {"text": "Кислотность", "is_correct": True},
                            {"text": "Температуру", "is_correct": False},
                            {"text": "Плотность", "is_correct": False},
                            {"text": "Давление", "is_correct": False}
                        ]
                    }
                ]
            },
            # Python - 4 ДЗ
            {
                "name": "Основы Python",
                "subject_name": "Python",
                "course": course_it,
                "questions": [
                    {
                        "text": "Какой тип данных используется для хранения текста в Python?",
                        "time_limit": 30,
                        "microtopic_number": 1,
                        "answers": [
                            {"text": "str", "is_correct": True},
                            {"text": "text", "is_correct": False},
                            {"text": "string", "is_correct": False},
                            {"text": "char", "is_correct": False}
                        ]
                    }
                ]
            },
            {
                "name": "Циклы и условия",
                "subject_name": "Python",
                "course": course_it,
                "questions": [
                    {
                        "text": "Какой оператор используется для цикла в Python?",
                        "time_limit": 30,
                        "microtopic_number": 2,
                        "answers": [
                            {"text": "for", "is_correct": True},
                            {"text": "loop", "is_correct": False},
                            {"text": "repeat", "is_correct": False},
                            {"text": "cycle", "is_correct": False}
                        ]
                    }
                ]
            },
            {
                "name": "Функции",
                "subject_name": "Python",
                "course": course_it,
                "questions": [
                    {
                        "text": "Как объявить функцию в Python?",
                        "time_limit": 30,
                        "microtopic_number": 3,
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
                "subject_name": "Python",
                "course": course_it,
                "questions": [
                    {
                        "text": "Как создать класс в Python?",
                        "time_limit": 30,
                        "microtopic_number": 4,
                        "answers": [
                            {"text": "class", "is_correct": True},
                            {"text": "object", "is_correct": False},
                            {"text": "struct", "is_correct": False},
                            {"text": "type", "is_correct": False}
                        ]
                    }
                ]
            },
            # Биология - 4 ДЗ
            {
                "name": "Строение клетки",
                "subject_name": "Биология",
                "course": course_ent,
                "questions": [
                    {
                        "text": "Что является основной структурной единицей живого организма?",
                        "time_limit": 30,
                        "microtopic_number": 1,
                        "answers": [
                            {"text": "Клетка", "is_correct": True},
                            {"text": "Ткань", "is_correct": False},
                            {"text": "Орган", "is_correct": False},
                            {"text": "Система органов", "is_correct": False}
                        ]
                    }
                ]
            },
            {
                "name": "Генетика и наследственность",
                "subject_name": "Биология",
                "course": course_ent,
                "questions": [
                    {
                        "text": "Кто открыл законы наследственности?",
                        "time_limit": 30,
                        "microtopic_number": 2,
                        "answers": [
                            {"text": "Грегор Мендель", "is_correct": True},
                            {"text": "Чарльз Дарвин", "is_correct": False},
                            {"text": "Луи Пастер", "is_correct": False},
                            {"text": "Александр Флеминг", "is_correct": False}
                        ]
                    }
                ]
            },
            {
                "name": "Эволюция и естественный отбор",
                "subject_name": "Биология",
                "course": course_ent,
                "questions": [
                    {
                        "text": "Кто является автором теории эволюции?",
                        "time_limit": 30,
                        "microtopic_number": 3,
                        "answers": [
                            {"text": "Чарльз Дарвин", "is_correct": True},
                            {"text": "Грегор Мендель", "is_correct": False},
                            {"text": "Жан-Батист Ламарк", "is_correct": False},
                            {"text": "Альфред Уоллес", "is_correct": False}
                        ]
                    }
                ]
            },
            {
                "name": "Экосистемы и биосфера",
                "subject_name": "Биология",
                "course": course_ent,
                "questions": [
                    {
                        "text": "Что такое экосистема?",
                        "time_limit": 30,
                        "microtopic_number": 4,
                        "answers": [
                            {"text": "Совокупность живых организмов и среды их обитания", "is_correct": True},
                            {"text": "Только живые организмы", "is_correct": False},
                            {"text": "Только неживая природа", "is_correct": False},
                            {"text": "Только растения", "is_correct": False}
                        ]
                    }
                ]
            },
            # Математика - 4 ДЗ
            {
                "name": "Основы математики",
                "subject_name": "Математика",
                "course": course_ent,
                "questions": [
                    {
                        "text": "Чему равен корень из 16?",
                        "time_limit": 30,
                        "microtopic_number": 1,
                        "answers": [
                            {"text": "4", "is_correct": True},
                            {"text": "8", "is_correct": False},
                            {"text": "2", "is_correct": False},
                            {"text": "16", "is_correct": False}
                        ]
                    }
                ]
            },
            {
                "name": "Алгебра",
                "subject_name": "Математика",
                "course": course_ent,
                "questions": [
                    {
                        "text": "Чему равно x в уравнении 2x + 4 = 10?",
                        "time_limit": 30,
                        "microtopic_number": 2,
                        "answers": [
                            {"text": "3", "is_correct": True},
                            {"text": "2", "is_correct": False},
                            {"text": "4", "is_correct": False},
                            {"text": "5", "is_correct": False}
                        ]
                    }
                ]
            },
            {
                "name": "Геометрия",
                "subject_name": "Математика",
                "course": course_ent,
                "questions": [
                    {
                        "text": "Сколько градусов в треугольнике?",
                        "time_limit": 30,
                        "microtopic_number": 3,
                        "answers": [
                            {"text": "180", "is_correct": True},
                            {"text": "90", "is_correct": False},
                            {"text": "360", "is_correct": False},
                            {"text": "270", "is_correct": False}
                        ]
                    }
                ]
            },
            {
                "name": "Тригонометрия",
                "subject_name": "Математика",
                "course": course_ent,
                "questions": [
                    {
                        "text": "Чему равен sin(90°)?",
                        "time_limit": 30,
                        "microtopic_number": 4,
                        "answers": [
                            {"text": "1", "is_correct": True},
                            {"text": "0", "is_correct": False},
                            {"text": "0.5", "is_correct": False},
                            {"text": "-1", "is_correct": False}
                        ]
                    }
                ]
            }
        ]

        created_homeworks_count = 0
        created_questions_count = 0
        created_answers_count = 0

        for hw_data in homework_data:
            try:
                # Находим предмет
                subject = created_subjects.get(hw_data["subject_name"])
                if not subject:
                    print(f"   ❌ Предмет '{hw_data['subject_name']}' не найден")
                    continue

                # Находим урок для этого предмета
                subject_lessons = await LessonRepository.get_by_subject(subject.id)
                if not subject_lessons:
                    print(f"   ❌ Не найдены уроки для предмета '{hw_data['subject_name']}'")
                    continue

                lesson = subject_lessons[0]  # Берем первый урок

                # Проверяем, существует ли уже такое ДЗ
                existing_homeworks = await HomeworkRepository.get_by_lesson(lesson.id)
                if any(hw.name == hw_data["name"] for hw in existing_homeworks):
                    print(f"   ⚠️  ДЗ '{hw_data['name']}' уже существует")
                    continue

                # Создаем домашнее задание
                homework = await HomeworkRepository.create(
                    name=hw_data["name"],
                    subject_id=subject.id,
                    lesson_id=lesson.id
                )

                print(f"   ✅ Создано ДЗ '{homework.name}' (ID: {homework.id})")
                created_homeworks_count += 1

                # Создаем вопросы
                question_repo = QuestionRepository()
                for question_data in hw_data["questions"]:
                    question = await question_repo.create(
                        homework_id=homework.id,
                        text=question_data["text"],
                        subject_id=subject.id,
                        microtopic_number=question_data.get("microtopic_number"),
                        time_limit=question_data["time_limit"]
                    )

                    created_questions_count += 1

                    # Создаем варианты ответов
                    await AnswerOptionRepository.create_multiple(
                        question.id,
                        question_data["answers"]
                    )

                    created_answers_count += len(question_data["answers"])

            except Exception as e:
                print(f"   ❌ Ошибка при создании ДЗ '{hw_data['name']}': {e}")

        print(f"📊 Создано домашних заданий: {created_homeworks_count}")
        print(f"📊 Создано вопросов: {created_questions_count}")
        print(f"📊 Создано вариантов ответов: {created_answers_count}")

    except Exception as e:
        print(f"❌ Ошибка при добавлении тестовых данных ДЗ: {e}")


async def add_test_bonus_tests():
    """Добавление тестовых бонусных тестов"""
    try:
        # Данные для тестовых бонусных тестов
        bonus_tests_data = [
            {
                "name": "Тест по алканам",
                "price": 100,
                "questions": [
                    {
                        "text": "Какое из следующих соединений является изомером бутана?",
                        "time_limit": 30,
                        "answers": [
                            {"text": "Пропан", "is_correct": False},
                            {"text": "2-метилпропан", "is_correct": True},
                            {"text": "Пентан", "is_correct": False},
                            {"text": "Этан", "is_correct": False}
                        ]
                    },
                    {
                        "text": "Какой тип изомерии характерен для алканов?",
                        "time_limit": 45,
                        "answers": [
                            {"text": "Геометрическая", "is_correct": False},
                            {"text": "Структурная", "is_correct": True},
                            {"text": "Оптическая", "is_correct": False},
                            {"text": "Таутомерия", "is_correct": False}
                        ]
                    },
                    {
                        "text": "Какая реакция характерна для алканов?",
                        "time_limit": 30,
                        "answers": [
                            {"text": "Присоединение", "is_correct": False},
                            {"text": "Замещение", "is_correct": True},
                            {"text": "Полимеризация", "is_correct": False},
                            {"text": "Конденсация", "is_correct": False}
                        ]
                    }
                ]
            },
            {
                "name": "Основы программирования",
                "price": 150,
                "questions": [
                    {
                        "text": "Что такое переменная в программировании?",
                        "time_limit": 30,
                        "answers": [
                            {"text": "Именованная область памяти", "is_correct": True},
                            {"text": "Функция", "is_correct": False},
                            {"text": "Класс", "is_correct": False},
                            {"text": "Модуль", "is_correct": False}
                        ]
                    },
                    {
                        "text": "Какой из языков является интерпретируемым?",
                        "time_limit": 30,
                        "answers": [
                            {"text": "C++", "is_correct": False},
                            {"text": "Java", "is_correct": False},
                            {"text": "Python", "is_correct": True},
                            {"text": "C#", "is_correct": False}
                        ]
                    }
                ]
            },
            {
                "name": "Математические основы",
                "price": 75,
                "questions": [
                    {
                        "text": "Чему равно значение π (пи) с точностью до двух знаков?",
                        "time_limit": 30,
                        "answers": [
                            {"text": "3.14", "is_correct": True},
                            {"text": "3.15", "is_correct": False},
                            {"text": "3.13", "is_correct": False},
                            {"text": "3.16", "is_correct": False}
                        ]
                    },
                    {
                        "text": "Какая формула используется для вычисления площади круга?",
                        "time_limit": 45,
                        "answers": [
                            {"text": "πr²", "is_correct": True},
                            {"text": "2πr", "is_correct": False},
                            {"text": "πd", "is_correct": False},
                            {"text": "r²", "is_correct": False}
                        ]
                    },
                    {
                        "text": "Сколько градусов в прямом угле?",
                        "time_limit": 20,
                        "answers": [
                            {"text": "90°", "is_correct": True},
                            {"text": "180°", "is_correct": False},
                            {"text": "45°", "is_correct": False},
                            {"text": "360°", "is_correct": False}
                        ]
                    }
                ]
            },
            {
                "name": "Физика: Механика",
                "price": 120,
                "questions": [
                    {
                        "text": "Какая единица измерения силы в СИ?",
                        "time_limit": 30,
                        "answers": [
                            {"text": "Ньютон", "is_correct": True},
                            {"text": "Джоуль", "is_correct": False},
                            {"text": "Ватт", "is_correct": False},
                            {"text": "Паскаль", "is_correct": False}
                        ]
                    },
                    {
                        "text": "Что описывает второй закон Ньютона?",
                        "time_limit": 45,
                        "answers": [
                            {"text": "F = ma", "is_correct": True},
                            {"text": "E = mc²", "is_correct": False},
                            {"text": "P = mv", "is_correct": False},
                            {"text": "W = Fs", "is_correct": False}
                        ]
                    }
                ]
            }
        ]

        created_bonus_tests_count = 0
        created_bonus_questions_count = 0
        created_bonus_answers_count = 0

        for test_data in bonus_tests_data:
            try:
                # Проверяем, существует ли уже такой бонусный тест
                existing_test = await BonusTestRepository.exists_by_name(test_data["name"])
                if existing_test:
                    print(f"   ⚠️  Бонусный тест '{test_data['name']}' уже существует")
                    continue

                # Создаем бонусный тест
                bonus_test = await BonusTestRepository.create(
                    name=test_data["name"],
                    price=test_data["price"]
                )

                print(f"   ✅ Создан бонусный тест '{bonus_test.name}' (ID: {bonus_test.id}, цена: {bonus_test.price} монет)")
                created_bonus_tests_count += 1

                # Создаем вопросы для бонусного теста
                for question_data in test_data["questions"]:
                    bonus_question_repo = BonusQuestionRepository()
                    question = await bonus_question_repo.create(
                        bonus_test_id=bonus_test.id,
                        text=question_data["text"],
                        time_limit=question_data["time_limit"]
                    )

                    created_bonus_questions_count += 1

                    # Создаем варианты ответов
                    await BonusAnswerOptionRepository.create_multiple(
                        question.id,
                        question_data["answers"]
                    )

                    created_bonus_answers_count += len(question_data["answers"])

            except Exception as e:
                print(f"   ❌ Ошибка при создании бонусного теста '{test_data['name']}': {e}")

        print(f"📊 Создано бонусных тестов: {created_bonus_tests_count}")
        print(f"📊 Создано бонусных вопросов: {created_bonus_questions_count}")
        print(f"📊 Создано бонусных вариантов ответов: {created_bonus_answers_count}")

    except Exception as e:
        print(f"❌ Ошибка при добавлении тестовых бонусных тестов: {e}")


async def add_test_month_tests(created_subjects, course_ent, course_it):
    """Добавление тестовых тестов месяца"""
    try:
        # Данные для тестовых тестов месяца
        month_tests_data = [
            {
                "name": "Сентябрь",
                "course": course_ent,
                "subject_name": "Математика",
                "microtopic_numbers": [1, 2, 3]  # Первые 3 микротемы
            },
            {
                "name": "Октябрь",
                "course": course_ent,
                "subject_name": "Математика",
                "microtopic_numbers": [2, 3, 4]  # Микротемы 2-4
            },
            {
                "name": "Сентябрь",
                "course": course_ent,
                "subject_name": "Химия",
                "microtopic_numbers": [1, 2]  # Первые 2 микротемы
            },
            {
                "name": "Октябрь",
                "course": course_ent,
                "subject_name": "Физика",
                "microtopic_numbers": [1, 2, 3, 4]  # Все 4 микротемы
            },
            {
                "name": "Сентябрь",
                "course": course_it,
                "subject_name": "Python",
                "microtopic_numbers": [1, 2]  # Первые 2 микротемы
            },
            {
                "name": "Октябрь",
                "course": course_it,
                "subject_name": "Python",
                "microtopic_numbers": [3, 4]  # Микротемы 3-4
            },
            {
                "name": "Сентябрь",
                "course": course_it,
                "subject_name": "JavaScript",
                "microtopic_numbers": [1, 2, 3]  # Первые 3 микротемы
            }
        ]

        created_month_tests_count = 0
        created_relations_count = 0

        for test_data in month_tests_data:
            try:
                # Находим предмет
                subject = created_subjects.get(test_data["subject_name"])
                if not subject:
                    print(f"   ❌ Предмет '{test_data['subject_name']}' не найден")
                    continue

                course = test_data["course"]
                if not course:
                    print(f"   ❌ Курс не найден для теста '{test_data['name']}'")
                    continue

                # Проверяем, существует ли уже такой тест месяца
                existing_test = await MonthTestRepository.exists_by_name_course_subject(
                    test_data["name"], course.id, subject.id
                )
                if existing_test:
                    print(f"   ⚠️  Тест месяца '{test_data['name']}' уже существует для {course.name}/{subject.name}")
                    continue

                # Создаем тест месяца
                month_test = await MonthTestRepository.create(
                    name=test_data["name"],
                    course_id=course.id,
                    subject_id=subject.id
                )

                print(f"   ✅ Создан тест месяца '{month_test.name}' для {course.name}/{subject.name} (ID: {month_test.id})")
                created_month_tests_count += 1

                # Привязываем микротемы
                relations = await MonthTestMicrotopicRepository.create_multiple(
                    month_test.id,
                    test_data["microtopic_numbers"]
                )

                created_relations_count += len(relations)
                numbers_text = ", ".join([str(num) for num in sorted(test_data["microtopic_numbers"])])
                print(f"      📌 Привязаны микротемы: {numbers_text}")

            except Exception as e:
                print(f"   ❌ Ошибка при создании теста месяца '{test_data['name']}': {e}")

        print(f"📊 Создано тестов месяца: {created_month_tests_count}")
        print(f"📊 Создано связей с микротемами: {created_relations_count}")

    except Exception as e:
        print(f"❌ Ошибка при добавлении тестовых тестов месяца: {e}")


async def add_test_homework_results():
    """Добавление тестовых результатов домашних заданий для демонстрации статистики"""
    try:
        # Получаем всех студентов
        students = await StudentRepository.get_all()
        if not students:
            print("   ❌ Не найдены студенты для создания результатов")
            return

        # Получаем все домашние задания
        homeworks = await HomeworkRepository.get_all()
        if not homeworks:
            print("   ❌ Не найдены домашние задания для создания результатов")
            return

        # Получаем все вопросы с вариантами ответов
        question_repo = QuestionRepository()
        questions = await question_repo.get_all()
        if not questions:
            print("   ❌ Не найдены вопросы для создания результатов")
            return

        created_results_count = 0
        created_question_results_count = 0

        # Создаем результаты для каждого студента
        for student in students:
            print(f"📊 Создаем результаты для студента '{student.user.name}':")

            # Получаем ДЗ только по предметам групп студента
            if not student.groups:
                print(f"   ⚠️  У студента {student.user.name} нет групп")
                continue

            # Собираем все предметы из групп студента
            subject_ids = []
            subject_names = []
            for group in student.groups:
                if group.subject:
                    subject_ids.append(group.subject_id)
                    subject_names.append(group.subject.name)

            if not subject_ids:
                print(f"   ⚠️  У студента {student.user.name} нет предметов в группах")
                continue

            subject_homeworks = [hw for hw in homeworks if hw.subject_id in subject_ids]
            if not subject_homeworks:
                print(f"   ⚠️  Нет ДЗ по предметам {', '.join(subject_names)}")
                continue

            import random
            if student.user.telegram_id == 955518340:  # Андрей Климов
                print(f"   Создаем результаты для {student.user.name}")
                max_homeworks = len(subject_homeworks)
                num_homeworks = max_homeworks  # Выполняет ВСЕ ДЗ
                student_homeworks = subject_homeworks  # Все ДЗ
                is_excellent_student = True
            elif student.user.telegram_id == 333444555:  # Айсулу Нурбекова
                print(f"   Создаем отличные результаты для {student.user.name}")
                max_homeworks = len(subject_homeworks)
                num_homeworks = max_homeworks  # Выполняет ВСЕ ДЗ
                student_homeworks = subject_homeworks  # Все ДЗ
                is_excellent_student = True
            else:
                # Разное количество ДЗ для разных студентов (от 1 до всех доступных)
                max_homeworks = len(subject_homeworks)
                num_homeworks = random.randint(1, max_homeworks)  # От 1 до всех ДЗ
                student_homeworks = random.sample(subject_homeworks, num_homeworks)  # Случайные ДЗ
                is_excellent_student = False

            print(f"   📚 Выполняет {num_homeworks} из {max_homeworks} ДЗ по предметам {', '.join(subject_names)}")

            for homework in student_homeworks:
                try:
                    # Получаем вопросы для этого ДЗ
                    homework_questions = await question_repo.get_by_homework(homework.id)
                    if not homework_questions:
                        continue

                    # Симулируем разные уровни успеха
                    if is_excellent_student:
                        success_rate = random.choice([0.9, 0.95, 1.0, 1.0, 1.0])  # В основном 100%
                    else:
                        success_rate = random.choice([0.5, 0.7, 0.8, 0.9, 1.0])  # 50%, 70%, 80%, 90%, 100%

                    total_questions = len(homework_questions)
                    correct_answers = int(total_questions * success_rate)

                    # Баллы начисляются только при 100% результате
                    points_earned = total_questions * 3 if success_rate == 1.0 else 0
                    points_awarded = success_rate == 1.0

                    # Создаем результат ДЗ
                    homework_result = await HomeworkResultRepository.create(
                        student_id=student.id,
                        homework_id=homework.id,
                        total_questions=total_questions,
                        correct_answers=correct_answers,
                        points_earned=points_earned,
                        is_first_attempt=True,
                        points_awarded=points_awarded
                    )

                    created_results_count += 1

                    # Создаем результаты для каждого вопроса
                    question_results_data = []
                    correct_count = 0

                    for i, question in enumerate(homework_questions):
                        # Получаем варианты ответов для вопроса
                        answer_options = await AnswerOptionRepository.get_by_question(question.id)
                        if not answer_options:
                            continue

                        # Определяем правильность ответа
                        is_correct = correct_count < correct_answers
                        if is_correct:
                            correct_count += 1

                        # Выбираем ответ (правильный или случайный неправильный)
                        if is_correct:
                            selected_answer = next((opt for opt in answer_options if opt.is_correct), None)
                        else:
                            wrong_answers = [opt for opt in answer_options if not opt.is_correct]
                            selected_answer = random.choice(wrong_answers) if wrong_answers else answer_options[0]

                        # Случайное время ответа (10-60 секунд)
                        time_spent = random.randint(10, 60)

                        question_results_data.append({
                            'question_id': question.id,
                            'selected_answer_id': selected_answer.id if selected_answer else None,
                            'is_correct': is_correct,
                            'time_spent': time_spent,
                            'microtopic_number': question.microtopic_number
                        })

                    # Создаем результаты вопросов
                    if question_results_data:
                        await QuestionResultRepository.create_multiple(
                            homework_result.id,
                            question_results_data
                        )
                        created_question_results_count += len(question_results_data)

                    result_percent = int(success_rate * 100)
                    print(f"   ✅ ДЗ '{homework.name}': {correct_answers}/{total_questions} ({result_percent}%) - {points_earned} баллов")

                    # Иногда создаем повторную попытку для студентов с неидеальным результатом
                    if success_rate < 1.0:
                        if is_excellent_student:
                            # Андрей Климов и Айсулу Нурбекова всегда исправляют на 100%
                            should_repeat = True
                            repeat_success_rate = 1.0
                        else:
                            should_repeat = random.choice([True, False])
                            repeat_success_rate = min(1.0, success_rate + 0.2)

                        if should_repeat:
                            # Повторная попытка с лучшим результатом
                            repeat_correct = int(total_questions * repeat_success_rate)
                            repeat_points = total_questions * 3 if repeat_success_rate == 1.0 else 0

                            repeat_result = await HomeworkResultRepository.create(
                                student_id=student.id,
                                homework_id=homework.id,
                                total_questions=total_questions,
                                correct_answers=repeat_correct,
                                points_earned=repeat_points,
                                is_first_attempt=False,
                                points_awarded=False  # Баллы уже были начислены в первой попытке
                            )

                            # Создаем улучшенные результаты вопросов
                            repeat_question_results = []
                            repeat_correct_count = 0

                            for question in homework_questions:
                                answer_options = await AnswerOptionRepository.get_by_question(question.id)
                                if not answer_options:
                                    continue

                                is_correct = repeat_correct_count < repeat_correct
                                if is_correct:
                                    repeat_correct_count += 1

                                if is_correct:
                                    selected_answer = next((opt for opt in answer_options if opt.is_correct), None)
                                else:
                                    wrong_answers = [opt for opt in answer_options if not opt.is_correct]
                                    selected_answer = random.choice(wrong_answers) if wrong_answers else answer_options[0]

                                time_spent = random.randint(8, 45)  # Быстрее во второй раз

                                repeat_question_results.append({
                                    'question_id': question.id,
                                    'selected_answer_id': selected_answer.id if selected_answer else None,
                                    'is_correct': is_correct,
                                    'time_spent': time_spent,
                                    'microtopic_number': question.microtopic_number
                                })

                            if repeat_question_results:
                                await QuestionResultRepository.create_multiple(
                                    repeat_result.id,
                                    repeat_question_results
                                )
                                created_question_results_count += len(repeat_question_results)

                            repeat_percent = int(repeat_success_rate * 100)
                            print(f"   🔄 Повтор '{homework.name}': {repeat_correct}/{total_questions} ({repeat_percent}%) - {repeat_points} баллов")
                            created_results_count += 1

                except Exception as e:
                    print(f"   ❌ Ошибка при создании результата для ДЗ '{homework.name}': {e}")

        print(f"📊 Создано результатов ДЗ: {created_results_count}")
        print(f"📊 Создано результатов вопросов: {created_question_results_count}")

    except Exception as e:
        print(f"❌ Ошибка при добавлении тестовых результатов ДЗ: {e}")


async def update_all_student_stats():
    """Обновление баллов и уровней всех студентов"""
    try:
        students = await StudentRepository.get_all()
        if not students:
            print("   ❌ Не найдены студенты для обновления статистики")
            return

        updated_count = 0
        for student in students:
            try:
                success = await StudentRepository.update_points_and_level(student.id)
                if success:
                    # Получаем обновленные данные
                    updated_student = await StudentRepository.get_by_id(student.id)
                    if updated_student:
                        print(f"   ✅ {updated_student.user.name}: {updated_student.points} баллов, уровень '{updated_student.level}'")
                        updated_count += 1
                else:
                    print(f"   ❌ Не удалось обновить статистику для студента {student.user.name}")
            except Exception as e:
                print(f"   ❌ Ошибка при обновлении статистики студента {student.user.name}: {e}")

        print(f"📊 Обновлена статистика для {updated_count} студентов")

    except Exception as e:
        print(f"❌ Ошибка при обновлении статистики студентов: {e}")


async def create_results_for_andrey():
    try:
        # Находим Андрея Климова
        andrey = await StudentRepository.get_by_telegram_id(955518340)
        if not andrey:
            print("   ❌ Андрей Климов не найден")
            return

        # Проверяем, что он в правильной группе (Python)
        has_python_group = False
        if andrey.groups:
            for group in andrey.groups:
                if group.subject and group.subject.name == "Python":
                    has_python_group = True
                    break

        if not has_python_group:
            print(f"   🔄 Добавляем Андрея в группу Python...")
            # Находим группу PY-1
            groups = await GroupRepository.get_all()
            python_group = next((g for g in groups if g.name == "PY-1"), None)
            if python_group:
                await StudentRepository.add_groups(andrey.id, [python_group.id])
                andrey = await StudentRepository.get_by_id(andrey.id)  # Обновляем данные
                print(f"   ✅ Андрей добавлен в группу {python_group.name}")
            else:
                print("   ❌ Группа PY-1 не найдена")
                return

        print(f"   👤 Создаем результаты для {andrey.user.name}")

        # Получаем все ДЗ по Python
        homeworks = await HomeworkRepository.get_all()
        # Находим ID предмета Python из групп Андрея
        python_subject_id = None
        for group in andrey.groups:
            if group.subject and group.subject.name == "Python":
                python_subject_id = group.subject.id
                break

        if not python_subject_id:
            print("   ❌ Не найден предмет Python в группах Андрея")
            return

        python_homeworks = [hw for hw in homeworks if hw.subject_id == python_subject_id]

        if not python_homeworks:
            print("   ❌ Нет ДЗ по Python")
            return

        question_repo = QuestionRepository()
        created_results = 0

        for homework in python_homeworks:
            # Проверяем, есть ли уже результат
            existing_results = await HomeworkResultRepository.get_by_student(andrey.id)
            homework_exists = any(result.homework_id == homework.id for result in existing_results)
            if homework_exists:
                print(f"   ⚠️ Результат для ДЗ '{homework.name}' уже существует")
                continue

            # Получаем вопросы для этого ДЗ
            homework_questions = await question_repo.get_by_homework(homework.id)
            if not homework_questions:
                continue

            total_questions = len(homework_questions)
            correct_answers = total_questions  # 100% результат
            points_earned = total_questions * 3  # Максимальные баллы

            # Создаем результат ДЗ
            homework_result = await HomeworkResultRepository.create(
                student_id=andrey.id,
                homework_id=homework.id,
                total_questions=total_questions,
                correct_answers=correct_answers,
                points_earned=points_earned,
                is_first_attempt=True,
                points_awarded=True
            )

            # Создаем результаты для каждого вопроса
            question_results_data = []

            for question in homework_questions:
                # Получаем варианты ответов для вопроса
                answer_options = await AnswerOptionRepository.get_by_question(question.id)
                if not answer_options:
                    continue

                # Выбираем правильный ответ
                correct_answer = next((opt for opt in answer_options if opt.is_correct), None)

                # Быстрое время ответа (как у опытного разработчика)
                import random
                time_spent = random.randint(5, 15)  # 5-15 секунд

                question_results_data.append({
                    'question_id': question.id,
                    'selected_answer_id': correct_answer.id if correct_answer else None,
                    'is_correct': True,
                    'time_spent': time_spent,
                    'microtopic_number': question.microtopic_number
                })

            # Создаем результаты вопросов
            if question_results_data:
                await QuestionResultRepository.create_multiple(
                    homework_result.id,
                    question_results_data
                )

            print(f"   ✅ ДЗ '{homework.name}': {correct_answers}/{total_questions} (100%) - {points_earned} баллов")
            created_results += 1

        # Обновляем баллы и уровень
        await StudentRepository.update_points_and_level(andrey.id)

        # Получаем финальные данные
        final_andrey = await StudentRepository.get_by_id(andrey.id)
        if final_andrey:
            print(f"   🎉 Итого создано результатов: {created_results}")
            print(f"   💎 Финальные баллы: {final_andrey.points}")
            print(f"   🏆 Финальный уровень: {final_andrey.level}")

    except Exception as e:
        print(f"   ❌ Ошибка при создании результатов для Андрея: {e}")


async def add_admin_roles(created_subjects, course_ent, course_it):
    """Добавление всех ролей для админов с соответствующими данными"""
    try:
        # ID админов (только Андрей Климов получает все роли)
        admin_ids = [955518340]
        admin_names = {
            955518340: "Андрей Климов"
        }

        for admin_telegram_id in admin_ids:
            admin_name = admin_names[admin_telegram_id]
            print(f"👑 Настройка ролей для админа: {admin_name}")

            # Получаем пользователя-админа
            admin_user = await UserRepository.get_by_telegram_id(admin_telegram_id)
            if not admin_user:
                print(f"   ❌ Админ с ID {admin_telegram_id} не найден")
                continue

            # 1. Добавляем роль студента
            print(f"   🎓 Добавление роли студента...")
            try:
                # Проверяем, есть ли уже профиль студента
                existing_student = await StudentRepository.get_by_user_id(admin_user.id)
                if not existing_student:
                    # Получаем первую группу для математики
                    math_groups = await GroupRepository.get_by_subject(created_subjects["Математика"].id)
                    if math_groups:
                        student = await StudentRepository.create(
                            user_id=admin_user.id,
                            tariff="premium"
                        )
                        # Привязываем к группе
                        await StudentRepository.set_groups(student.id, [math_groups[0].id])
                        print(f"      ✅ Создан профиль студента (ID: {student.id}, группа: {math_groups[0].name})")
                    else:
                        print(f"      ❌ Не найдены группы для математики")
                else:
                    print(f"      ⚠️ Профиль студента уже существует (ID: {existing_student.id})")
            except Exception as e:
                print(f"      ❌ Ошибка при создании студента: {e}")

            # 2. Добавляем роль куратора
            print(f"   👨‍🎓 Добавление роли куратора...")
            try:
                # Проверяем, есть ли уже профиль куратора
                existing_curator = await CuratorRepository.get_by_user_id(admin_user.id)
                if not existing_curator:
                    curator = await CuratorRepository.create(
                        user_id=admin_user.id,
                        course_id=course_ent.id,
                        subject_id=created_subjects["Математика"].id
                    )
                    print(f"      ✅ Создан профиль куратора (ID: {curator.id})")

                    # Добавляем куратора в группы математики
                    math_groups = await GroupRepository.get_by_subject(created_subjects["Математика"].id)
                    for group in math_groups[:2]:  # Добавляем в первые 2 группы
                        await CuratorRepository.add_curator_to_group(curator.id, group.id)
                        print(f"      ✅ Добавлен в группу: {group.name}")
                else:
                    print(f"      ⚠️ Профиль куратора уже существует (ID: {existing_curator.id})")
            except Exception as e:
                print(f"      ❌ Ошибка при создании куратора: {e}")

            # 3. Добавляем роль преподавателя
            print(f"   👨‍🏫 Добавление роли преподавателя...")
            try:
                # Проверяем, есть ли уже профиль преподавателя
                existing_teacher = await TeacherRepository.get_by_user_id(admin_user.id)
                if not existing_teacher:
                    # Получаем группу Python для IT курса
                    python_groups = await GroupRepository.get_by_subject(created_subjects["Python"].id)
                    if python_groups:
                        teacher = await TeacherRepository.create(
                            user_id=admin_user.id,
                            course_id=course_it.id,
                            subject_id=created_subjects["Python"].id
                        )

                        # Добавляем преподавателя в группу через M2M связь
                        success = await TeacherRepository.add_teacher_to_group(teacher.id, python_groups[0].id)
                        if success:
                            print(f"      ✅ Создан профиль преподавателя (ID: {teacher.id}, предмет: Python, группа: {python_groups[0].name})")
                        else:
                            print(f"      ⚠️ Преподаватель создан, но не удалось привязать к группе {python_groups[0].name}")
                    else:
                        print(f"      ❌ Не найдены группы для Python")
                else:
                    print(f"      ⚠️ Профиль преподавателя уже существует (ID: {existing_teacher.id})")
            except Exception as e:
                print(f"      ❌ Ошибка при создании преподавателя: {e}")

            # 4. Добавляем роль менеджера
            print(f"   👔 Добавление роли менеджера...")
            try:
                # Проверяем, есть ли уже профиль менеджера
                existing_manager = await ManagerRepository.get_by_user_id(admin_user.id)
                if not existing_manager:
                    manager = await ManagerRepository.create(user_id=admin_user.id)
                    print(f"      ✅ Создан профиль менеджера (ID: {manager.id})")
                else:
                    print(f"      ⚠️ Профиль менеджера уже существует (ID: {existing_manager.id})")
            except Exception as e:
                print(f"      ❌ Ошибка при создании менеджера: {e}")

            print(f"   🎉 Все роли настроены для {admin_name}")

        print(f"👑 Настройка ролей для всех админов завершена!")

    except Exception as e:
        print(f"❌ Ошибка при добавлении ролей админам: {e}")


async def assign_students_to_courses(created_subjects, course_ent, course_it):
    """Привязать студентов к курсам на основе их предметов"""
    if not course_ent or not course_it:
        print("⚠️ Курсы не найдены, пропускаем привязку студентов")
        return

    # Получаем всех студентов
    students = await StudentRepository.get_all()

    for student in students:
        if not student.groups:
            continue

        # Собираем все предметы из групп студента
        student_subjects = set()
        for group in student.groups:
            if group.subject:
                student_subjects.add(group.subject.name)

        course_ids = []

        # Определяем к каким курсам относятся предметы студента
        for subject_name in student_subjects:
            if subject_name in ["Математика", "Физика", "История Казахстана", "Химия", "Биология"]:
                if course_ent.id not in course_ids:
                    course_ids.append(course_ent.id)

            if subject_name in ["Python", "JavaScript", "Java", "Математика"]:
                if course_it.id not in course_ids:
                    course_ids.append(course_it.id)

        # Привязываем студента к курсам
        if course_ids:
            success = await StudentRepository.set_courses(student.id, course_ids)
            if success:
                course_names = []
                if course_ent.id in course_ids:
                    course_names.append("ЕНТ")
                if course_it.id in course_ids:
                    course_names.append("IT")
                print(f"✅ Студент '{student.user.name}' привязан к курсам: {', '.join(course_names)}")
            else:
                print(f"❌ Ошибка привязки студента '{student.user.name}' к курсам")


if __name__ == "__main__":
    asyncio.run(add_initial_data())
