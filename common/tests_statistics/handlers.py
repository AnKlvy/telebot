from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from .states import TestsStatisticsStates
from .keyboards import (
    get_tests_statistics_menu_kb,
    get_groups_kb,
    get_month_kb,
    get_students_kb,
    get_back_kb
)
from .menu import show_tests_statistics_menu
from common.statistics import (
    get_test_results,
    format_test_result,
    format_test_comparison
)
from ..keyboards import get_main_menu_back_button

router = Router()

# Обработчик для главного меню статистики тестов
@router.callback_query(F.data == "tests_statistics")
async def show_tests_statistics(callback: CallbackQuery, state: FSMContext):
    """Показать меню статистики тестов"""
    await show_tests_statistics_menu(callback, state)

# Обработчики для возврата в меню
@router.callback_query(F.data == "back_to_tests_statistics")
async def back_to_tests_statistics(callback: CallbackQuery, state: FSMContext):
    """Вернуться в меню статистики тестов"""
    await show_tests_statistics_menu(callback, state)

# Обработчики для входного теста курса
@router.callback_query(F.data == "stats_course_entry_test")
async def show_course_entry_groups(callback: CallbackQuery, state: FSMContext):
    """Показать группы для входного теста курса"""
    await callback.message.edit_text(
        "Выберите группу для просмотра статистики входного теста курса:",
        reply_markup=get_groups_kb("course_entry")
    )
    await state.set_state(TestsStatisticsStates.select_group)

@router.callback_query(TestsStatisticsStates.select_group, F.data.startswith("course_entry_group_"))
async def show_course_entry_statistics(callback: CallbackQuery, state: FSMContext):
    """Показать статистику входного теста курса для группы"""
    group_id = callback.data.replace("course_entry_group_", "")
    await show_test_students_statistics(callback, state, "course_entry", group_id)

@router.callback_query(F.data.startswith("course_entry_student_"))
async def show_course_entry_student_statistics(callback: CallbackQuery, state: FSMContext):
    """Показать статистику входного теста курса для конкретного ученика"""
    # Формат: course_entry_student_GROUP_ID_STUDENT_ID
    parts = callback.data.split("_")
    group_id = parts[3]
    student_id = parts[4]
    await show_student_test_statistics(callback, state, "course_entry", student_id, group_id)

# Обработчики для входного теста месяца
@router.callback_query(F.data == "stats_month_entry_test")
async def show_month_entry_groups(callback: CallbackQuery, state: FSMContext):
    """Показать группы для входного теста месяца"""
    await callback.message.edit_text(
        "Выберите группу для просмотра статистики входного теста месяца:",
        reply_markup=get_groups_kb("month_entry")
    )
    await state.set_state(TestsStatisticsStates.select_group)

@router.callback_query(TestsStatisticsStates.select_group, F.data.startswith("month_entry_group_"))
async def show_month_entry_months(callback: CallbackQuery, state: FSMContext):
    """Показать месяцы для входного теста месяца"""
    group_id = callback.data.replace("month_entry_group_", "")
    
    await state.update_data(selected_group=group_id)
    
    await callback.message.edit_text(
        "Выберите месяц для просмотра статистики входного теста:",
        reply_markup=get_month_kb("month_entry", group_id)
    )
    await state.set_state(TestsStatisticsStates.select_month)

@router.callback_query(F.data.startswith("back_to_month_entry_groups"))
async def back_to_month_entry_groups(callback: CallbackQuery, state: FSMContext):
    """Вернуться к выбору группы для входного теста месяца"""
    await show_month_entry_groups(callback, state)

@router.callback_query(TestsStatisticsStates.select_month, F.data.startswith("month_entry_month_"))
async def show_month_entry_statistics(callback: CallbackQuery, state: FSMContext):
    """Показать статистику входного теста месяца"""
    # Формат: month_entry_month_GROUP_ID_MONTH_ID
    parts = callback.data.split("_")
    group_id = parts[3]
    month_id = parts[4]
    await show_test_students_statistics(callback, state, "month_entry", group_id, month_id)

@router.callback_query(F.data.startswith("month_entry_student_"))
async def show_month_entry_student_statistics(callback: CallbackQuery, state: FSMContext):
    """Показать статистику входного теста месяца для конкретного ученика"""
    # Формат: month_entry_student_GROUP_ID_MONTH_ID_STUDENT_ID
    parts = callback.data.split("_")
    group_id = parts[3]
    month_id = parts[4]
    student_id = parts[5]
    await show_student_test_statistics(callback, state, "month_entry", student_id, group_id, month_id)

# Обработчики для контрольного теста месяца
@router.callback_query(F.data == "stats_month_control_test")
async def show_month_control_groups(callback: CallbackQuery, state: FSMContext):
    """Показать группы для контрольного теста месяца"""
    await callback.message.edit_text(
        "Выберите группу для просмотра статистики контрольного теста месяца:",
        reply_markup=get_groups_kb("month_control")
    )
    await state.set_state(TestsStatisticsStates.select_group)

@router.callback_query(TestsStatisticsStates.select_group, F.data.startswith("month_control_group_"))
async def show_month_control_months(callback: CallbackQuery, state: FSMContext):
    """Показать месяцы для контрольного теста месяца"""
    group_id = callback.data.replace("month_control_group_", "")
    
    await state.update_data(selected_group=group_id)
    
    await callback.message.edit_text(
        "Выберите месяц для просмотра статистики контрольного теста:",
        reply_markup=get_month_kb("month_control", group_id)
    )
    await state.set_state(TestsStatisticsStates.select_month)

@router.callback_query(F.data.startswith("back_to_month_control_groups"))
async def back_to_month_control_groups(callback: CallbackQuery, state: FSMContext):
    """Вернуться к выбору группы для контрольного теста месяца"""
    await show_month_control_groups(callback, state)

@router.callback_query(TestsStatisticsStates.select_month, F.data.startswith("month_control_month_"))
async def show_month_control_statistics(callback: CallbackQuery, state: FSMContext):
    """Показать статистику контрольного теста месяца"""
    # Формат: month_control_month_GROUP_ID_MONTH_ID
    parts = callback.data.split("_")
    group_id = parts[3]
    month_id = parts[4]
    await show_test_students_statistics(callback, state, "month_control", group_id, month_id)

@router.callback_query(F.data.startswith("compare_tests_"))
async def show_tests_comparison(callback: CallbackQuery, state: FSMContext):
    """Показать сравнение входного и контрольного тестов"""
    # Формат: compare_tests_GROUP_ID_MONTH_ID
    parts = callback.data.split("_")
    group_id = parts[2]
    month_id = parts[3]
    
    # Получаем результаты тестов из общего компонента
    # В реальном приложении здесь будет запрос к базе данных
    student_id = "student1"  # Пример ID студента
    entry_test_id = f"month_entry_chem_{month_id}"
    control_test_id = f"month_control_chem_{month_id}"
    
    entry_results = get_test_results(entry_test_id, student_id)
    control_results = get_test_results(control_test_id, student_id)
    
    # Форматируем сравнение результатов тестов
    result_text = format_test_comparison(
        entry_results,
        control_results,
        subject_name="Химия",
        month=month_id
    )
    
    await callback.message.edit_text(
        result_text,
        reply_markup=get_back_kb()
    )
    await state.set_state(TestsStatisticsStates.statistics_result)

# Обработчики для пробного ЕНТ
@router.callback_query(F.data == "stats_ent_test")
async def show_ent_groups(callback: CallbackQuery, state: FSMContext):
    """Показать группы для пробного ЕНТ"""
    await callback.message.edit_text(
        "Выберите группу для просмотра статистики пробного ЕНТ:",
        reply_markup=get_groups_kb("ent")
    )
    await state.set_state(TestsStatisticsStates.select_group)

@router.callback_query(TestsStatisticsStates.select_group, F.data.startswith("ent_group_"))
async def show_ent_students(callback: CallbackQuery, state: FSMContext):
    """Показать студентов для пробного ЕНТ"""
    group_id = callback.data.replace("ent_group_", "")
    
    await state.update_data(selected_group=group_id)
    
    await callback.message.edit_text(
        "Выберите ученика для просмотра статистики пробного ЕНТ:",
        reply_markup=get_students_kb("ent", group_id)
    )
    await state.set_state(TestsStatisticsStates.select_student)

@router.callback_query(F.data.startswith("back_to_ent_groups"))
async def back_to_ent_groups(callback: CallbackQuery, state: FSMContext):
    """Вернуться к выбору группы для пробного ЕНТ"""
    await show_ent_groups(callback, state)

@router.callback_query(TestsStatisticsStates.select_student, F.data.startswith("ent_student_"))
async def show_ent_statistics(callback: CallbackQuery, state: FSMContext):
    """Показать статистику пробного ЕНТ для студента"""
    # Формат: ent_student_GROUP_ID_STUDENT_ID
    parts = callback.data.split("_")
    group_id = parts[2]
    student_id = parts[3]
    await show_student_test_statistics(callback, state, "ent", student_id, group_id)

async def show_student_test_statistics(
    callback: CallbackQuery, 
    state: FSMContext, 
    test_type: str, 
    student_id: str, 
    group_id: str = None, 
    month_id: str = None
):
    """
    Общая функция для отображения статистики теста по конкретному ученику
    
    Args:
        callback: Объект CallbackQuery
        state: Контекст состояния FSM
        test_type: Тип теста (course_entry, month_entry, month_control, ent)
        student_id: ID студента
        group_id: ID группы (опционально)
        month_id: ID месяца (опционально)
    """
    print(f"DEBUG: show_student_test_statistics вызвана с параметрами: test_type={test_type}, student_id={student_id}, group_id={group_id}, month_id={month_id}")
    
    # Определяем ID теста и предмет в зависимости от типа теста
    if test_type == "course_entry":
        test_id = "course_entry_chem"
        subject_name = "Химия"
    elif test_type == "month_entry":
        test_id = f"month_entry_chem_{month_id}"
        subject_name = "Химия"
    elif test_type == "month_control":
        test_id = f"month_control_chem_{month_id}"
        subject_name = "Химия"
    elif test_type == "ent":
        test_id = "course_entry_kz"
        subject_name = "История Казахстана"
    else:
        test_id = ""
        subject_name = "Неизвестный предмет"
    
    print(f"DEBUG: Сформирован test_id: {test_id}")
    
    # Получаем результаты теста из общего компонента
    from common.statistics import get_test_results
    test_results = get_test_results(test_id, student_id)
    
    print(f"DEBUG: Получены результаты теста: {test_results}")
    
    # Форматируем результаты теста
    from common.statistics import format_test_result
    result_text = format_test_result(
        test_results, 
        subject_name=subject_name, 
        test_type=test_type,
        month=month_id
    )
    
    print(f"DEBUG: Сформирован текст результата: {result_text}")
    
    # Добавляем информацию о группе
    group_name = group_id.replace("_", " ").title() if group_id else "Неизвестная группа"
    result_text = result_text.replace("курса пройден", f"{group_name} курса пройден")
    
    from common.tests_statistics.keyboards import get_back_kb
    await callback.message.edit_text(
        result_text,
        reply_markup=get_back_kb()
    )
    await state.set_state(TestsStatisticsStates.statistics_result)

async def show_test_students_statistics(
    callback: CallbackQuery, 
    state: FSMContext, 
    test_type: str, 
    group_id: str, 
    month_id: str = None, 
    title: str = None
):
    """
    Общая функция для отображения статистики теста по студентам
    
    Args:
        callback: Объект CallbackQuery
        state: Контекст состояния FSM
        test_type: Тип теста (course_entry, month_entry, month_control)
        group_id: ID группы
        month_id: ID месяца (опционально)
        title: Заголовок сообщения (опционально)
    """
    # В реальном приложении здесь будет запрос к базе данных
    # для получения статистики по группе и месяцу
    
    # Определяем списки студентов в зависимости от типа теста
    if test_type == "course_entry":
        completed_students = ["Мадияр Сапаров", "Диана Нурланова"]
        not_completed_students = ["Артем Осипов", "Арман Сериков"]
    elif test_type == "month_entry":
        completed_students = ["Мадияр Сапаров"]
        not_completed_students = ["Артем Осипов", "Диана Нурланова", "Арман Сериков"]
    elif test_type == "month_control":
        completed_students = ["Мадияр Сапаров", "Диана Нурланова"]
        not_completed_students = ["Артем Осипов", "Арман Сериков"]
    else:
        completed_students = []
        not_completed_students = []
    
    # Формируем заголовок сообщения
    if not title:
        if test_type == "course_entry":
            title = "📊 Статистика входного теста курса"
        elif test_type == "month_entry":
            title = f"📊 Статистика входного теста месяца {month_id}"
        elif test_type == "month_control":
            title = f"📊 Статистика контрольного теста месяца {month_id}"
        else:
            title = "📊 Статистика теста"
    
    # Формируем текст сообщения
    result_text = f"{title}\n\n"
    result_text += f"Группа: {group_id.replace('_', ' ').title()}\n\n"
    
    result_text += "✅ Прошли тест:\n"
    for i, student in enumerate(completed_students, 1):
        result_text += f"{i}. {student}\n"
    
    result_text += "\n❌ Не прошли тест:\n"
    for i, student in enumerate(not_completed_students, 1):
        result_text += f"{i}. {student}\n"
    
    # Добавляем кнопки для просмотра детальной статистики по ученикам
    buttons = []
    for student in completed_students:
        student_id = "student1" if student == "Мадияр Сапаров" else "student3"
        callback_data = f"{test_type}_student_{group_id}"
        if month_id:
            callback_data += f"_{month_id}"
        callback_data += f"_{student_id}"
        
        buttons.append([
            InlineKeyboardButton(
                text=f"📊 {student}",
                callback_data=callback_data
            )
        ])
    
    buttons.extend(get_main_menu_back_button())
    
    await callback.message.edit_text(
        result_text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )
    await state.set_state(TestsStatisticsStates.statistics_result)
