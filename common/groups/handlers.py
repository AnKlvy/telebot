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

    print(f"🔍 ЛОГИРОВАНИЕ show_group_students:")
    print(f"   📞 callback.data: {callback.data}")
    print(f"   👤 user_id: {callback.from_user.id}")
    print(f"   🎭 role: {role}")
    print(f"   🔄 current_state: {current_state}")
    print(f"   💾 FSM data: {data}")

    # Проверяем, это новый выбор группы или возврат назад
    if callback.data.startswith(f"{role}_group_"):
        # Новый выбор группы
        group_id_str = callback.data.replace(f"{role}_group_", "")
        print(f"   ✅ НОВЫЙ ВЫБОР ГРУППЫ: {group_id_str}")
    elif callback.data == "back" and data.get('selected_group'):
        # Возврат назад, используем сохраненные данные
        group_id_str = str(data.get('selected_group'))
        print(f"   🔄 ВОЗВРАТ НАЗАД: используем сохраненную группу {group_id_str}")
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

    # Проверяем, является ли student_id числом (реальный ID из БД) или строкой (хардкод)
    try:
        student_id = int(student_id_str)
        # Получаем реального студента из базы данных
        from database import StudentRepository, HomeworkResultRepository

        student_obj = await StudentRepository.get_by_id(student_id)

        if student_obj:
            # Получаем статистику студента
            homework_results = await HomeworkResultRepository.get_by_student(student_id)

            # Подсчитываем статистику
            total_homeworks = len(homework_results)
            total_points = sum(result.points_earned for result in homework_results)

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

            # Процент выполнения (примерный расчет)
            completion_percentage = min(100, total_homeworks * 5) if total_homeworks > 0 else 0

            student = {
                "name": student_obj.user.name,
                "telegram": f"@{student_obj.user.telegram_id}",
                "subject": student_obj.group.subject.name if student_obj.group and student_obj.group.subject else "Не указан",
                "points": total_points,
                "level": level,
                "homeworks_completed": total_homeworks,
                "last_homework_date": last_homework_date,
                "completion_percentage": completion_percentage
            }
        else:
            student = {
                "name": "Студент не найден",
                "telegram": "Не указан",
                "subject": "Не указан",
                "points": 0,
                "level": "Не определен",
                "homeworks_completed": 0,
                "last_homework_date": "Нет данных",
                "completion_percentage": 0
            }

    except (ValueError, Exception) as e:
        print(f"Ошибка при получении данных студента: {e}")
        # Хардкодим данные для совместимости со старыми ID
        if student_id_str == "1":
            student = {
                "name": "Аружан Ахметова",
                "telegram": "@aruzhan_chem",
                "subject": "Химия",
                "points": 870,
                "level": "🧪 Практик",
                "homeworks_completed": 28,
                "last_homework_date": "14.05.2025",
                "completion_percentage": 30
            }
        elif student_id_str == "2":
            student = {
                "name": "Мадияр Сапаров",
                "telegram": "@madiyar_bio",
                "subject": "Биология",
                "points": 920,
                "level": "🔬 Исследователь",
                "homeworks_completed": 32,
                "last_homework_date": "15.05.2025",
                "completion_percentage": 35
            }
        elif student_id_str == "3":
            student = {
                "name": "Диана Ержанова",
                "telegram": "@diana_history",
                "subject": "История",
                "points": 750,
                "level": "📚 Теоретик",
                "homeworks_completed": 25,
                "last_homework_date": "12.05.2025",
                "completion_percentage": 28
            }
        else:
            student = {
                "name": "Неизвестный ученик",
                "telegram": "Не указан",
                "subject": "Не указан",
                "points": 0,
                "level": "Не определен",
                "homeworks_completed": 0,
                "last_homework_date": "Нет данных",
                "completion_percentage": 0
            }

    # Сохраняем данные в состоянии
    await state.update_data(selected_student_id=student_id_str, student=student)

    # Формируем сообщение
    await callback.message.edit_text(
        f"👤 {student['name']}\n"
        f"📞 Telegram: {student['telegram']}\n"
        f"📚 Предмет: {student['subject']}\n"
        f"🎯 Баллы: {student['points']}\n"
        f"📈 Уровень: {student['level']}\n"
        f"📋 Выполнено ДЗ: {student['homeworks_completed']} (с учетом повторных)\n"
        f"🕓 Последнее выполненное ДЗ: {student['last_homework_date']}\n"
        f"🕓% выполнения ДЗ: {student['completion_percentage']}%",
        reply_markup=get_student_profile_kb(role)
    )
