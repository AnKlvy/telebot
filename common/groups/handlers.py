from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from .states import GroupStates
from .keyboards import get_groups_kb, get_students_kb, get_student_profile_kb
from common.keyboards import get_main_menu_back_button

async def show_groups(callback: CallbackQuery, state: FSMContext, role: str):
    """
    Базовый обработчик для показа списка групп

    Args:
        callback: Объект CallbackQuery
        state: Контекст состояния FSM
        role: Роль пользователя (curator)
    """
    # Получаем telegram_id пользователя для куратора и учителя
    user_telegram_id = callback.from_user.id if (role == "curator" or role == "teacher") else None

    print(f"🔍 HANDLER: show_groups для {role}, telegram_id={user_telegram_id}")

    await callback.message.edit_text(
        "Выберите группу для просмотра:",
        reply_markup=await get_groups_kb(role, user_telegram_id)
    )

async def show_group_students(callback: CallbackQuery, state: FSMContext, role: str):
    """
    Базовый обработчик для показа списка студентов группы

    Args:
        callback: Объект CallbackQuery
        state: Контекст состояния FSM
        role: Роль пользователя (curator, teacher)
    """
    current_state = await state.get_state()
    data = await state.get_data()


    # Проверяем, это новый выбор группы или возврат назад
    if callback.data.startswith(f"{role}_group_"):
        # Новый выбор группы
        group_id_str = callback.data.replace(f"{role}_group_", "")
    elif callback.data == "back" and data.get('selected_group'):
        # Возврат назад, используем сохраненные данные
        group_id_str = str(data.get('selected_group'))
    else:
        print(f"   ❌ ОШИБКА: Не удалось определить group_id")
        print(f"   📋 callback.data не начинается с '{role}_group_' и нет сохраненной группы")
        await callback.message.edit_text(
            "❌ Ошибка: не удалось определить группу",
            reply_markup=get_main_menu_back_button()
        )
        return

    # Проверяем, является ли group_id числом (реальный ID из БД) или строкой (хардкод)
    try:
        group_id = int(group_id_str)
        # Получаем реальную группу из базы данных
        from database import GroupRepository
        group = await GroupRepository.get_by_id(group_id)

        if group:
            group_name = f"{group.name}"
            if group.subject:
                group_name += f" ({group.subject.name})"
        else:
            group_name = "Неизвестная группа"

        print(f"   📖 Группа из БД: ID={group_id}, Название={group_name}")

    except ValueError:
        # Это не числовой ID - ошибка, так как хардкод убран
        print(f"   ❌ Неверный group_id: {group_id_str}. Ожидается числовой ID")
        await callback.message.edit_text(
            "❌ Ошибка: неверный идентификатор группы",
            reply_markup=get_main_menu_back_button()
        )
        return

    await state.update_data(selected_group=group_id, group_name=group_name)
    print(f"   💾 Сохранено в состоянии: selected_group={group_id}, group_name={group_name}")

    await callback.message.edit_text(
        f"Группа: {group_name}\n\n"
        "Выберите ученика для просмотра информации:",
        reply_markup=await get_students_kb(role, group_id)
    )
    print(f"   ✅ Сообщение обновлено, показаны студенты группы {group_id}")

async def show_student_profile(callback: CallbackQuery, state: FSMContext, role: str):
    """
    Базовый обработчик для показа профиля студента

    Args:
        callback: Объект CallbackQuery
        state: Контекст состояния FSM
        role: Роль пользователя (curator, teacher)
    """
    # Получаем ID студента из callback_data
    student_id_str = callback.data.replace(f"{role}_student_", "")
    print(f"🔍 Получен callback_data: {callback.data}")
    print(f"🔍 Извлеченный student_id_str: {student_id_str}")

    # Проверяем, является ли student_id числом (реальный ID из БД) или строкой (хардкод)
    try:
        student_id = int(student_id_str)
        print(f"🔍 Преобразованный student_id: {student_id}")

        # Получаем реального студента из базы данных
        from database import StudentRepository, HomeworkResultRepository

        print(f"🔍 Запрашиваем студента из БД с ID: {student_id}")
        student_obj = await StudentRepository.get_by_id(student_id)
        print(f"🔍 Результат запроса студента: {student_obj is not None}")

        if student_obj:
            print(f"✅ Студент найден: {student_obj.user.name}")

            # Получаем статистику студента
            homework_results = await HomeworkResultRepository.get_by_student(student_id)
            print(f"📊 Найдено результатов ДЗ: {len(homework_results)}")

            # Подсчитываем статистику
            # Считаем уникальные ДЗ (не повторные попытки)
            unique_homework_ids = set(result.homework_id for result in homework_results)
            unique_homeworks_count = len(unique_homework_ids)

            total_homeworks = len(homework_results)  # Всего попыток (включая повторные)
            total_points = sum(result.points_earned for result in homework_results)
            print(f"📊 Общая статистика: Всего попыток={total_homeworks}, Уникальных ДЗ={unique_homeworks_count}, Баллы={total_points}")

            # Определяем уровень на основе баллов
            if total_points >= 1000:
                level = "🏆 Мастер"
            elif total_points >= 500:
                level = "🔬 Исследователь"
            elif total_points >= 200:
                level = "🧪 Практик"
            else:
                level = "📚 Новичок"

            # Последнее выполненное ДЗ
            last_homework_date = "Нет данных"
            if homework_results:
                last_result = max(homework_results, key=lambda x: x.completed_at)
                last_homework_date = last_result.completed_at.strftime("%d.%m.%Y")

            # Процент выполнения (правильный расчет)
            # Получаем общее количество доступных ДЗ для студента
            try:
                from database import HomeworkRepository

                # Получаем все ДЗ по предметам студента
                all_available_homeworks = 0
                if student_obj.groups:
                    subject_ids = []
                    for group in student_obj.groups:
                        if group.subject and group.subject.id not in subject_ids:
                            subject_ids.append(group.subject.id)

                    for subject_id in subject_ids:
                        subject_homeworks = await HomeworkRepository.get_by_subject(subject_id)
                        all_available_homeworks += len(subject_homeworks)

                # Рассчитываем процент: (уникальных выполнено / всего доступных) * 100
                if all_available_homeworks > 0:
                    completion_percentage = round((unique_homeworks_count / all_available_homeworks) * 100, 1)
                else:
                    completion_percentage = 0

                print(f"📊 Расчет процента: {unique_homeworks_count} уникальных выполнено / {all_available_homeworks} доступно = {completion_percentage}%")

            except Exception as e:
                print(f"❌ Ошибка при расчете процента выполнения: {e}")
                completion_percentage = 0

            # Получаем предметы из групп студента
            subjects = []
            if student_obj.groups:
                for group in student_obj.groups:
                    if group.subject and group.subject.name not in subjects:
                        subjects.append(group.subject.name)

            subject_str = ", ".join(subjects) if subjects else "Не указан"

            student = {
                "name": student_obj.user.name,
                "telegram": f"@{student_obj.user.telegram_id}",
                "subject": subject_str,
                "points": total_points,
                "level": level,
                "homeworks_completed": total_homeworks,
                "unique_homeworks_completed": unique_homeworks_count,
                "last_homework_date": last_homework_date,
                "completion_percentage": completion_percentage
            }
        else:
            print(f"❌ Студент с ID {student_id} не найден в базе данных")
            await callback.message.edit_text(
                f"❌ Студент не найден\n"
                f"ID студента: {student_id}\n\n"
                "Возможно, студент был удален или произошла ошибка.\n"
                "Попробуйте выбрать другого студента или обратитесь к администратору.",
                reply_markup=get_student_profile_kb(role)
            )
            return

    except (ValueError, Exception) as e:
        print(f"❌ Ошибка при получении данных студента ID {student_id_str}: {e}")
        import traceback
        traceback.print_exc()

        # Возвращаем ошибку вместо захардкоженных данных
        await callback.message.edit_text(
            f"❌ Ошибка при загрузке данных студента\n"
            f"ID студента: {student_id_str}\n"
            f"Ошибка: {str(e)}\n\n"
            "Попробуйте выбрать студента заново или обратитесь к администратору.",
            reply_markup=get_student_profile_kb(role)
        )
        return

    # Сохраняем данные в состоянии
    await state.update_data(selected_student_id=student_id_str, student=student)

    # Формируем сообщение
    await callback.message.edit_text(
        f"👤 {student['name']}\n"
        f"📞 Telegram: {student['telegram']}\n"
        f"📚 Предмет: {student['subject']}\n"
        f"🎯 Баллы: {student['points']}\n"
        f"📈 Уровень: {student['level']}\n"
        f"📋 Выполнено ДЗ: {student['unique_homeworks_completed']} уникальных ({student['homeworks_completed']} всего попыток)\n"
        f"🕓 Последнее выполненное ДЗ: {student['last_homework_date']}\n"
        f"📊 % выполнения ДЗ: {student['completion_percentage']}%",
        reply_markup=get_student_profile_kb(role)
    )
