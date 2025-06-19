"""
Создание групп и пользователей
"""
from database import (
    GroupRepository, UserRepository, StudentRepository, CuratorRepository,
    TeacherRepository, ManagerRepository
)


async def create_user_if_not_exists(telegram_id, name, role):
    """Создать пользователя, если он не существует"""
    existing_user = await UserRepository.get_by_telegram_id(telegram_id)
    if not existing_user:
        user = await UserRepository.create(
            telegram_id=telegram_id,
            name=name,
            role=role
        )
        print(f"   ✅ {role.title()} '{user.name}' создан (ID: {user.id})")
        return user, True
    else:
        print(f"   ⚠️ {role.title()} '{existing_user.name}' уже существует (ID: {existing_user.id})")
        return existing_user, False


async def create_groups_and_users(created_subjects):
    """Создание групп и пользователей"""
    try:
        # Создание групп
        print("👥 Создание групп...")
        groups_data = [
            # ЕНТ группы
            {"name": "М-1", "subject": "Математика"},
            {"name": "М-2", "subject": "Математика"},
            {"name": "Ф-1", "subject": "Физика"},
            {"name": "ИК-1", "subject": "История Казахстана"},
            {"name": "Х-1", "subject": "Химия"},
            {"name": "Б-1", "subject": "Биология"},
            # IT группы
            {"name": "PY-1", "subject": "Python"},
            {"name": "PY-2", "subject": "Python"},
            {"name": "JS-1", "subject": "JavaScript"},
            {"name": "JAVA-1", "subject": "Java"},
        ]

        created_groups = {}
        for group_data in groups_data:
            subject_name = group_data["subject"]
            if subject_name in created_subjects:
                try:
                    group = await GroupRepository.create(
                        name=group_data["name"],
                        subject_id=created_subjects[subject_name].id
                    )
                    created_groups[group.name] = group
                    print(f"   ✅ Группа '{group.name}' создана для предмета '{subject_name}' (ID: {group.id})")
                except ValueError as e:
                    # Группа уже существует, получаем её из базы
                    existing_groups = await GroupRepository.get_by_subject(created_subjects[subject_name].id)
                    existing_group = next((g for g in existing_groups if g.name == group_data["name"]), None)
                    if existing_group:
                        created_groups[existing_group.name] = existing_group
                        print(f"   ⚠️ Группа '{existing_group.name}' уже существует для предмета '{subject_name}' (ID: {existing_group.id})")
                    else:
                        print(f"   ❌ Ошибка при создании группы '{group_data['name']}': {e}")

        # Создание пользователей
        print("👤 Создание пользователей...")

        # Админ (получит все роли)
        admin_user, _ = await create_user_if_not_exists(955518340, "Андрей Климов", "admin")

        # Менеджеры
        managers_data = [
            {"telegram_id": 111222333, "name": "Алия Сейтова"},
            {"telegram_id": 444555666, "name": "Данияр Жумабеков"},
            {"telegram_id": 7265679697, "name": "Медина Махамбет"},
        ]

        for manager_data in managers_data:
            user, is_new = await create_user_if_not_exists(
                manager_data["telegram_id"],
                manager_data["name"],
                "manager"
            )
            if is_new:
                manager = await ManagerRepository.create(user_id=user.id)
                print(f"      ✅ Профиль менеджера создан (Manager ID: {manager.id})")

        # Кураторы
        curators_data = [
            {"telegram_id": 777888999, "name": "Айгерим Касымова", "groups": ["М-1", "М-2"]},
            {"telegram_id": 123456789, "name": "Ерлан Нурланов", "groups": ["Ф-1", "ИК-1"]},
        ]

        for curator_data in curators_data:
            user, is_new = await create_user_if_not_exists(
                curator_data["telegram_id"],
                curator_data["name"],
                "curator"
            )
            if is_new:
                # Создаем куратора без привязки к конкретному курсу/предмету
                curator = await CuratorRepository.create(user_id=user.id)

                # Привязываем к группам
                for group_name in curator_data["groups"]:
                    if group_name in created_groups:
                        await CuratorRepository.add_curator_to_group(curator.id, created_groups[group_name].id)
                        print(f"      ✅ Добавлен в группу '{group_name}'")

                print(f"      ✅ Профиль куратора создан (Curator ID: {curator.id})")

        # Преподаватели
        teachers_data = [
            {"telegram_id": 987654321, "name": "Асель Токтарова", "subject": "Python", "groups": ["PY-1"]},
            {"telegram_id": 555666777, "name": "Максат Ибрагимов", "subject": "JavaScript", "groups": ["JS-1"]},
        ]

        for teacher_data in teachers_data:
            user, is_new = await create_user_if_not_exists(
                teacher_data["telegram_id"],
                teacher_data["name"],
                "teacher"
            )

            if is_new:
                subject_name = teacher_data["subject"]
                if subject_name in created_subjects:
                    teacher = await TeacherRepository.create(
                        user_id=user.id,
                        subject_id=created_subjects[subject_name].id
                    )

                    # Привязываем к группам
                    for group_name in teacher_data["groups"]:
                        if group_name in created_groups:
                            await TeacherRepository.add_teacher_to_group(teacher.id, created_groups[group_name].id)
                            print(f"      ✅ Добавлен в группу '{group_name}'")

                    print(f"      ✅ Профиль преподавателя создан (Teacher ID: {teacher.id})")

        # Студенты
        students_data = [
            {"telegram_id": 333444555, "name": "Муханбетжан Олжас", "groups": ["PY-1", "М-2"], "tariff": "premium"},
            {"telegram_id": 666777888, "name": "Аружан Ахметова", "groups": ["М-1"], "tariff": "standard"},
            {"telegram_id": 999000111, "name": "Бекзат Сериков", "groups": ["PY-2"], "tariff": "premium"},
            {"telegram_id": 222333444, "name": "Динара Жанибекова", "groups": ["JS-1"], "tariff": "standard"},
            {"telegram_id": 888999000, "name": "Ерасыл Мухамедов", "groups": ["М-2"], "tariff": "premium"},
        ]

        for student_data in students_data:
            user, is_new = await create_user_if_not_exists(
                student_data["telegram_id"],
                student_data["name"],
                "student"
            )

            if is_new:
                student = await StudentRepository.create(
                    user_id=user.id,
                    tariff=student_data["tariff"]
                )
                print(f"      ✅ Профиль студента создан (Student ID: {student.id})")
            else:
                # Получаем существующего студента
                student = await StudentRepository.get_by_user_id(user.id)
                print(f"      ⚠️ Student '{student_data['name']}' уже существует (ID: {student.id})")

            # Привязываем к группам (для новых и существующих студентов)
            group_ids = []
            for group_name in student_data["groups"]:
                if group_name in created_groups:
                    group_ids.append(created_groups[group_name].id)

            if group_ids:
                await StudentRepository.set_groups(student.id, group_ids)
                group_names = ", ".join(student_data["groups"])
                print(f"      ✅ Обновлены группы: {group_names} (Student ID: {student.id})")

        print(f"👥 Создание групп и пользователей завершено!")

    except Exception as e:
        print(f"❌ Ошибка при создании групп и пользователей: {e}")
