from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from .keyboards import (
    get_analytics_menu_kb, get_groups_for_analytics_kb,
    get_students_for_analytics_kb, get_groups_by_curator_kb,
    get_back_to_student_analytics_kb
)
from common.utils import check_if_id_in_callback_data
from common.statistics import (
    get_student_microtopics_detailed,
    get_student_strong_weak_summary,
    show_student_analytics
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

    if curator_id and role == "manager":
        # Если выбран куратор, показываем его группы
        keyboard = await get_groups_by_curator_kb(curator_id)
    else:
        # Иначе показываем все группы
        keyboard = await get_groups_for_analytics_kb(role)

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
    group_id = await check_if_id_in_callback_data("analytics_group_", callback, state, "group")

    
    students_kb = await get_students_for_analytics_kb(group_id)
    await callback.message.edit_text(
        "Выберите ученика для просмотра статистики:",
        reply_markup=students_kb
    )
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

    if curator_id and role == "manager":
        # Если выбран куратор, показываем его группы
        keyboard = await get_groups_by_curator_kb(curator_id)
    else:
        # Иначе показываем все группы
        keyboard = await get_groups_for_analytics_kb(role)

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


