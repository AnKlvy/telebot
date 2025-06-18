"""
Добавление ролей для админов
"""
from database import (
    UserRepository, StudentRepository, CuratorRepository, 
    TeacherRepository, ManagerRepository, GroupRepository
)


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
