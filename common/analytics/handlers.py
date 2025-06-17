from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from .keyboards import (
    get_analytics_menu_kb, get_groups_for_analytics_kb,
    get_students_for_analytics_kb, get_groups_by_curator_kb,
    get_back_to_student_analytics_kb, get_subjects_for_analytics_kb,
    get_back_to_analytics_kb, get_subject_microtopics_kb,
    get_back_to_subject_analytics_kb, get_general_microtopics_kb,
    get_back_to_general_analytics_kb, get_group_analytics_kb
)
from common.utils import check_if_id_in_callback_data
from common.statistics import (
    get_student_microtopics_detailed,
    get_student_strong_weak_summary,
    show_student_analytics,
    get_subject_stats,
    format_subject_stats,
    get_subject_microtopics_detailed,
    get_subject_microtopics_summary,
    get_general_stats,
    format_general_stats,
    get_general_microtopics_detailed,
    get_general_microtopics_summary,
    show_group_microtopics_detailed,
    show_group_rating
)


async def show_analytics_menu(callback: CallbackQuery, state: FSMContext, role: str):
    """
    Базовый обработчик для показа меню аналитики
    
    Args:
        callback: Объект CallbackQuery
        state: Контекст состояния FSM
        role: Роль пользователя (curator)
    """
    await callback.message.edit_text(
        "Выберите тип аналитики:",
        reply_markup=get_analytics_menu_kb(role)
    )
    # Удаляем установку состояния

async def select_group_for_student_analytics(callback: CallbackQuery, state: FSMContext, role: str):
    """
    Базовый обработчик для выбора группы для статистики по ученику

    Args:
        callback: Объект CallbackQuery
        state: Контекст состояния FSM
        role: Роль пользователя (curator)
    """
    # Получаем ID выбранного куратора из состояния
    data = await state.get_data()
    curator_id = data.get('selected_curator')

    print(f"🔍 DEBUG select_group_for_student_analytics: role={role}, curator_id={curator_id}, data={data}")

    if curator_id and role == "manager":
        # Если выбран куратор, показываем его группы
        keyboard = await get_groups_by_curator_kb(curator_id)
    else:
        # Передаем Telegram ID для кураторов, учителей и админов в контексте куратора
        # Проверяем состояние, чтобы понять, работает ли админ в контексте куратора
        current_state = await state.get_state()
        is_role_specific_context = (
            role == "curator" or
            role == "teacher" or
            (role == "admin" and current_state and "CuratorAnalyticsStates" in current_state)
        )

        user_telegram_id = callback.from_user.id if is_role_specific_context else None
        print(f"🔍 ANALYTICS: role={role}, state={current_state}, is_role_specific_context={is_role_specific_context}, telegram_id={user_telegram_id}")

        keyboard = await get_groups_for_analytics_kb(role, user_telegram_id)

    await callback.message.edit_text(
        "Выберите группу ученика:",
        reply_markup=keyboard
    )
    # Удаляем установку состояния

async def select_student_for_analytics(callback: CallbackQuery, state: FSMContext, role: str):
    """
    Базовый обработчик для выбора ученика для статистики

    Args:
        callback: Объект CallbackQuery
        state: Контекст состояния FSM
        role: Роль пользователя (curator)
    """
    current_state = await state.get_state()
    print(f"🔍 ЛОГИРОВАНИЕ select_student_for_analytics:")
    print(f"   📞 callback.data: {callback.data}")
    print(f"   👤 user_id: {callback.from_user.id}")
    print(f"   🎭 role: {role}")
    print(f"   🔄 current_state: {current_state}")

    # Получаем все данные из состояния
    data = await state.get_data()
    print(f"   💾 FSM data: {data}")

    saved_group_id = data.get('selected_group')
    print(f"   🏷️ saved_group_id: {saved_group_id}")

    group_id = None

    if callback.data.startswith("analytics_group_"):
        # Если это новый выбор группы, извлекаем ID из callback
        group_id = await check_if_id_in_callback_data("analytics_group_", callback, state, "group")
        # Сохраняем ID группы в состоянии для возможности возврата
        await state.update_data(selected_group=group_id)
        print(f"   ✅ НОВЫЙ ВЫБОР ГРУППЫ: {group_id}, сохранено в состоянии")
    elif saved_group_id:
        # Если это возврат назад, используем сохраненный ID группы
        group_id = saved_group_id
        print(f"   🔄 ВОЗВРАТ НАЗАД: используем сохраненную группу {group_id}")
    else:
        print(f"   ❌ ОШИБКА: Не удалось определить group_id")
        print(f"   📋 callback.data не начинается с 'analytics_group_' и saved_group_id пустой")
        await callback.message.edit_text(
            "❌ Ошибка: не удалось определить группу",
            reply_markup=get_back_to_analytics_kb()
        )
        return

    print(f"   🎯 ИТОГОВЫЙ group_id: {group_id}")

    # Получаем студентов группы
    students_kb = await get_students_for_analytics_kb(group_id)
    print(f"   👥 Получена клавиатура студентов для группы {group_id}")

    await callback.message.edit_text(
        "Выберите ученика для просмотра статистики:",
        reply_markup=students_kb
    )
    print(f"   ✅ Сообщение обновлено, ожидаем выбор ученика")
    # Удаляем установку состояния


async def select_group_for_group_analytics(callback: CallbackQuery, state: FSMContext, role: str):
    """
    Базовый обработчик для выбора группы для статистики по группе

    Args:
        callback: Объект CallbackQuery
        state: Контекст состояния FSM
        role: Роль пользователя (curator)
    """
    # Получаем ID выбранного куратора из состояния
    data = await state.get_data()
    curator_id = data.get('selected_curator')

    print(f"🔍 DEBUG select_group_for_group_analytics: role={role}, curator_id={curator_id}, data={data}")

    if curator_id and role == "manager":
        # Если выбран куратор, показываем его группы
        keyboard = await get_groups_by_curator_kb(curator_id)
    else:
        # Передаем Telegram ID для кураторов, учителей и админов в контексте куратора
        # Проверяем состояние, чтобы понять, работает ли админ в контексте куратора
        current_state = await state.get_state()
        is_role_specific_context = (
            role == "curator" or
            role == "teacher" or
            (role == "admin" and current_state and "CuratorAnalyticsStates" in current_state)
        )

        user_telegram_id = callback.from_user.id if is_role_specific_context else None
        print(f"🔍 ANALYTICS: role={role}, state={current_state}, is_role_specific_context={is_role_specific_context}, telegram_id={user_telegram_id}")

        keyboard = await get_groups_for_analytics_kb(role, user_telegram_id)

    await callback.message.edit_text(
        "Выберите группу для просмотра статистики:",
        reply_markup=keyboard
    )
    # Удаляем установку состояния


async def show_microtopics_detailed(callback: CallbackQuery, state: FSMContext):
    """
    Показать детальную статистику по микротемам

    Args:
        callback: Объект CallbackQuery
        state: Контекст состояния FSM
    """
    # Извлекаем student_id и subject_id из callback_data
    # Формат: microtopics_detailed_STUDENT_ID_SUBJECT_ID
    parts = callback.data.split("_")
    if len(parts) >= 4:
        student_id = int(parts[2])
        subject_id = int(parts[3])

        # Получаем детальную статистику
        result_text = await get_student_microtopics_detailed(student_id, subject_id)

        await callback.message.edit_text(
            result_text,
            reply_markup=get_back_to_student_analytics_kb(student_id, subject_id)
        )
    else:
        await callback.message.edit_text(
            "❌ Ошибка в данных запроса",
            reply_markup=get_back_to_student_analytics_kb(0, 0)
        )


async def show_microtopics_summary(callback: CallbackQuery, state: FSMContext):
    """
    Показать сводку по сильным и слабым темам

    Args:
        callback: Объект CallbackQuery
        state: Контекст состояния FSM
    """
    # Извлекаем student_id и subject_id из callback_data
    # Формат: microtopics_summary_STUDENT_ID_SUBJECT_ID
    parts = callback.data.split("_")
    if len(parts) >= 4:
        student_id = int(parts[2])
        subject_id = int(parts[3])

        # Получаем сводку по сильным и слабым темам
        result_text = await get_student_strong_weak_summary(student_id, subject_id)

        await callback.message.edit_text(
            result_text,
            reply_markup=get_back_to_student_analytics_kb(student_id, subject_id)
        )
    else:
        await callback.message.edit_text(
            "❌ Ошибка в данных запроса",
            reply_markup=get_back_to_student_analytics_kb(0, 0)
        )


async def back_to_student_analytics(callback: CallbackQuery, state: FSMContext, role: str):
    """
    Вернуться к основной статистике студента

    Args:
        callback: Объект CallbackQuery
        state: Контекст состояния FSM
        role: Роль пользователя
    """
    # Извлекаем student_id из callback_data
    # Формат: back_to_student_STUDENT_ID
    parts = callback.data.split("_")
    if len(parts) >= 4:
        student_id = parts[3]

        # Имитируем callback для показа статистики студента
        callback.data = f"analytics_student_{student_id}"
        await show_student_analytics(callback, state, role)
    else:
        from .keyboards import get_back_to_analytics_kb
        await callback.message.edit_text(
            "❌ Ошибка в данных запроса",
            reply_markup=get_back_to_analytics_kb()
        )


async def select_subject_for_analytics(callback: CallbackQuery, state: FSMContext, role: str):
    """
    Базовый обработчик для выбора предмета для статистики

    Args:
        callback: Объект CallbackQuery
        state: Контекст состояния FSM
        role: Роль пользователя (curator, manager)
    """
    await callback.message.edit_text(
        "Выберите предмет для просмотра статистики:",
        reply_markup=await get_subjects_for_analytics_kb(role)
    )


async def show_subject_analytics(callback: CallbackQuery, state: FSMContext, role: str):
    """
    Базовый обработчик для показа статистики по предмету

    Args:
        callback: Объект CallbackQuery
        state: Контекст состояния FSM
        role: Роль пользователя (curator, manager)
    """
    subject_id = await check_if_id_in_callback_data("analytics_subject_", callback, state, "subject")

    # Получаем данные о предмете
    subject_data = await get_subject_stats(subject_id)

    # Формируем базовую информацию о предмете
    result_text = f"📚 Предмет: {subject_data['name']}\n\n"
    result_text += f"👨‍👩‍👧‍👦 Количество групп: {len(subject_data['groups'])}\n"

    if subject_data['groups']:
        # Вычисляем средний процент выполнения ДЗ
        avg_homework = sum(group['homework_completion'] for group in subject_data['groups']) / len(subject_data['groups'])
        result_text += f"📊 Средний % выполнения ДЗ: {avg_homework:.1f}%\n\n"

        # Показываем список групп
        result_text += "📋 Группы:\n"
        for group in subject_data['groups']:
            result_text += f"• {group['name']} - {group['homework_completion']}%\n"
    else:
        result_text += "❌ Группы не найдены\n"

    result_text += "\nВыберите, что хотите посмотреть:"

    await callback.message.edit_text(
        result_text,
        reply_markup=get_subject_microtopics_kb(int(subject_id))
    )


async def show_subject_microtopics_detailed(callback: CallbackQuery, state: FSMContext):
    """
    Показать детальную статистику по микротемам предмета

    Args:
        callback: Объект CallbackQuery
        state: Контекст состояния FSM
    """
    # Извлекаем subject_id из callback_data
    # Формат: subject_microtopics_detailed_SUBJECT_ID
    parts = callback.data.split("_")
    if len(parts) >= 4:
        subject_id = int(parts[3])

        # Получаем детальную статистику
        result_text = await get_subject_microtopics_detailed(subject_id)

        await callback.message.edit_text(
            result_text,
            reply_markup=get_back_to_subject_analytics_kb(subject_id)
        )
    else:
        await callback.message.edit_text(
            "❌ Ошибка в данных запроса",
            reply_markup=get_back_to_analytics_kb()
        )


async def show_subject_microtopics_summary(callback: CallbackQuery, state: FSMContext):
    """
    Показать сводку по сильным и слабым темам предмета

    Args:
        callback: Объект CallbackQuery
        state: Контекст состояния FSM
    """
    # Извлекаем subject_id из callback_data
    # Формат: subject_microtopics_summary_SUBJECT_ID
    parts = callback.data.split("_")
    if len(parts) >= 4:
        subject_id = int(parts[3])

        # Получаем сводку по сильным и слабым темам
        result_text = await get_subject_microtopics_summary(subject_id)

        await callback.message.edit_text(
            result_text,
            reply_markup=get_back_to_subject_analytics_kb(subject_id)
        )
    else:
        await callback.message.edit_text(
            "❌ Ошибка в данных запроса",
            reply_markup=get_back_to_analytics_kb()
        )


