from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
import logging
from .keyboards import (
    get_tests_statistics_menu_kb,
    get_groups_kb,
    get_month_kb,
    get_students_kb,
    get_back_kb,
    get_curator_groups_kb
)
from .menu import show_tests_statistics_menu
from common.statistics import (
    get_test_results,
    format_test_result,
    format_test_comparison
)
from ..keyboards import get_main_menu_back_button
from ..utils import check_if_id_in_callback_data

# Настройка логгера
logger = logging.getLogger(__name__)

router = Router()

# Обработчик для главного меню статистики тестов
@router.callback_query(F.data == "tests_statistics")
async def show_tests_statistics(callback: CallbackQuery, state: FSMContext):
    """Показать меню статистики тестов"""
    current_state = await state.get_state()
    logger.info(f"ВЫЗОВ: show_tests_statistics, user_id={callback.from_user.id}, текущее состояние={current_state}, callback_data={callback.data}")
    await show_tests_statistics_menu(callback, state)

# Обработчики для возврата в меню
@router.callback_query(F.data == "back_to_tests_statistics")
async def back_to_tests_statistics(callback: CallbackQuery, state: FSMContext):
    """Вернуться в меню статистики тестов"""
    current_state = await state.get_state()
    logger.info(f"ВЫЗОВ: back_to_tests_statistics, user_id={callback.from_user.id}, текущее состояние={current_state}, callback_data={callback.data}")
    await show_tests_statistics_menu(callback, state)

# Обработчики для входного теста курса
@router.callback_query(F.data == "stats_course_entry_test")
async def show_course_entry_groups(callback: CallbackQuery, state: FSMContext):
    """Показать группы для входного теста курса"""
    current_state = await state.get_state()
    logger.info(f"ВЫЗОВ: show_course_entry_groups, user_id={callback.from_user.id}, текущее состояние={current_state}, callback_data={callback.data}")

    # Определяем роль пользователя по состоянию
    role = "curator"  # По умолчанию
    if current_state and "Teacher" in current_state:
        role = "teacher"
    elif current_state and "Curator" in current_state:
        role = "curator"

    # Получаем группы в зависимости от роли
    from database import CuratorRepository, TeacherRepository, UserRepository

    user = await UserRepository.get_by_telegram_id(callback.from_user.id)
    if not user:
        await callback.message.edit_text(
            "❌ Пользователь не найден в системе",
            reply_markup=get_back_kb()
        )
        return

    groups = []

    # Проверяем роль и получаем соответствующие группы
    if role == "curator":
        # Получаем профиль куратора по user_id
        curator = await CuratorRepository.get_by_user_id(user.id)
        if curator:
            groups = await CuratorRepository.get_curator_groups(curator.id)
        else:
            logger.info(f"Пользователь {user.name} не является куратором")

    elif role == "teacher":
        # Получаем профиль учителя по user_id
        teacher = await TeacherRepository.get_by_user_id(user.id)
        if teacher:
            groups = await TeacherRepository.get_teacher_groups(teacher.id)
        else:
            logger.info(f"Пользователь {user.name} не является учителем")

    if not groups:
        await callback.message.edit_text(
            "❌ У вас нет назначенных групп",
            reply_markup=get_back_kb()
        )
        return

    await callback.message.edit_text(
        "Выберите группу для просмотра статистики входного теста курса:",
        reply_markup=await get_curator_groups_kb("course_entry", groups)
    )

@router.callback_query(F.data.startswith("course_entry_group_"))
async def show_course_entry_statistics(callback: CallbackQuery, state: FSMContext):
    """Показать статистику входного теста курса для группы"""
    current_state = await state.get_state()
    logger.info(f"ВЫЗОВ: show_course_entry_statistics, user_id={callback.from_user.id}, текущее состояние={current_state}, callback_data={callback.data}")

    try:
        group_id = int(await check_if_id_in_callback_data("course_entry_group_", callback, state, "group_id"))
        await show_course_entry_test_statistics(callback, state, group_id)
    except ValueError:
        await callback.message.edit_text(
            "❌ Ошибка: неверный ID группы",
            reply_markup=get_back_kb()
        )

@router.callback_query(F.data.startswith("course_entry_student_"))
async def show_course_entry_student_statistics(callback: CallbackQuery, state: FSMContext):
    """Показать статистику входного теста курса для конкретного ученика"""
    current_state = await state.get_state()
    logger.info(f"ВЫЗОВ: show_course_entry_student_statistics, user_id={callback.from_user.id}, текущее состояние={current_state}, callback_data={callback.data}")

    try:
        # Формат: course_entry_student_GROUP_ID_STUDENT_ID
        parts = callback.data.split("_")
        group_id = int(parts[3])
        student_id = int(parts[4])
        await show_course_entry_student_detail(callback, state, group_id, student_id)
    except (ValueError, IndexError):
        await callback.message.edit_text(
            "❌ Ошибка: неверные параметры",
            reply_markup=get_back_kb()
        )

# Обработчики для входного теста месяца
@router.callback_query(F.data == "stats_month_entry_test")
async def show_month_entry_groups(callback: CallbackQuery, state: FSMContext):
    """Показать группы для входного теста месяца"""
    current_state = await state.get_state()
    logger.info(f"ВЫЗОВ: show_month_entry_groups, user_id={callback.from_user.id}, текущее состояние={current_state}, callback_data={callback.data}")

    # Определяем роль пользователя по состоянию
    role = "curator"  # По умолчанию
    if current_state and "Teacher" in current_state:
        role = "teacher"
    elif current_state and "Curator" in current_state:
        role = "curator"

    # Получаем группы в зависимости от роли
    from database import CuratorRepository, TeacherRepository, UserRepository

    user = await UserRepository.get_by_telegram_id(callback.from_user.id)
    if not user:
        await callback.message.edit_text(
            "❌ Пользователь не найден в системе",
            reply_markup=get_back_kb()
        )
        return

    groups = []

    # Проверяем роль и получаем соответствующие группы
    if role == "curator":
        # Получаем профиль куратора по user_id
        curator = await CuratorRepository.get_by_user_id(user.id)
        if curator:
            groups = await CuratorRepository.get_curator_groups(curator.id)
        else:
            logger.info(f"Пользователь {user.name} не является куратором")

    elif role == "teacher":
        # Получаем профиль учителя по user_id
        teacher = await TeacherRepository.get_by_user_id(user.id)
        if teacher:
            groups = await TeacherRepository.get_teacher_groups(teacher.id)
        else:
            logger.info(f"Пользователь {user.name} не является учителем")

    if not groups:
        await callback.message.edit_text(
            "❌ У вас нет назначенных групп",
            reply_markup=get_back_kb()
        )
        return

    await callback.message.edit_text(
        "Выберите группу для просмотра статистики входного теста месяца:",
        reply_markup=await get_curator_groups_kb("month_entry", groups)
    )

@router.callback_query(F.data.startswith("month_entry_group_"))
async def show_month_entry_months(callback: CallbackQuery, state: FSMContext):
    """Показать месяцы для входного теста месяца"""
    current_state = await state.get_state()
    logger.info(f"ВЫЗОВ: show_month_entry_months, user_id={callback.from_user.id}, текущее состояние={current_state}, callback_data={callback.data}")

    try:
        group_id = int(await check_if_id_in_callback_data("month_entry_group_", callback, state, "group_id"))
        await show_month_entry_test_months(callback, state, group_id)
    except ValueError:
        await callback.message.edit_text(
            "❌ Ошибка: неверный ID группы",
            reply_markup=get_back_kb()
        )

@router.callback_query(F.data.startswith("back_to_month_entry_groups"))
async def back_to_month_entry_groups(callback: CallbackQuery, state: FSMContext):
    """Вернуться к выбору группы для входного теста месяца"""
    current_state = await state.get_state()
    logger.info(f"ВЫЗОВ: back_to_month_entry_groups, user_id={callback.from_user.id}, текущее состояние={current_state}, callback_data={callback.data}")
    await show_month_entry_groups(callback, state)

@router.callback_query(F.data.startswith("month_entry_month_"))
async def show_month_entry_statistics(callback: CallbackQuery, state: FSMContext):
    """Показать статистику входного теста месяца"""
    current_state = await state.get_state()
    logger.info(f"ВЫЗОВ: show_month_entry_statistics, user_id={callback.from_user.id}, текущее состояние={current_state}, callback_data={callback.data}")

    try:
        # Формат: month_entry_month_GROUP_ID_MONTH_TEST_ID
        parts = callback.data.split("_")
        group_id = int(parts[3])
        month_test_id = int(parts[4])
        await show_month_entry_test_statistics(callback, state, group_id, month_test_id)
    except (ValueError, IndexError):
        await callback.message.edit_text(
            "❌ Ошибка: неверные параметры",
            reply_markup=get_back_kb()
        )

@router.callback_query(F.data.startswith("month_entry_student_"))
async def show_month_entry_student_statistics(callback: CallbackQuery, state: FSMContext):
    """Показать статистику входного теста месяца для конкретного ученика"""
    current_state = await state.get_state()
    logger.info(f"ВЫЗОВ: show_month_entry_student_statistics, user_id={callback.from_user.id}, текущее состояние={current_state}, callback_data={callback.data}")

    try:
        # Формат: month_entry_student_GROUP_ID_MONTH_TEST_ID_STUDENT_ID
        parts = callback.data.split("_")
        group_id = int(parts[3])
        month_test_id = int(parts[4])
        student_id = int(parts[5])
        await show_month_entry_student_detail(callback, state, group_id, month_test_id, student_id)
    except (ValueError, IndexError):
        await callback.message.edit_text(
            "❌ Ошибка: неверные параметры",
            reply_markup=get_back_kb()
        )

# Обработчики для контрольного теста месяца
@router.callback_query(F.data == "stats_month_control_test")
async def show_month_control_groups(callback: CallbackQuery, state: FSMContext):
    """Показать группы для контрольного теста месяца"""
    current_state = await state.get_state()
    logger.info(f"ВЫЗОВ: show_month_control_groups, user_id={callback.from_user.id}, текущее состояние={current_state}, callback_data={callback.data}")

    # Определяем роль пользователя по состоянию
    role = "curator"  # По умолчанию
    if current_state and "Teacher" in current_state:
        role = "teacher"
    elif current_state and "Curator" in current_state:
        role = "curator"

    # Получаем группы в зависимости от роли
    from database import CuratorRepository, TeacherRepository, UserRepository

    user = await UserRepository.get_by_telegram_id(callback.from_user.id)
    if not user:
        await callback.message.edit_text(
            "❌ Пользователь не найден в системе",
            reply_markup=get_back_kb()
        )
        return

    groups = []

    # Проверяем роль и получаем соответствующие группы
    if role == "curator":
        # Получаем профиль куратора по user_id
        curator = await CuratorRepository.get_by_user_id(user.id)
        if curator:
            groups = await CuratorRepository.get_curator_groups(curator.id)
        else:
            logger.info(f"Пользователь {user.name} не является куратором")

    elif role == "teacher":
        # Получаем профиль учителя по user_id
        teacher = await TeacherRepository.get_by_user_id(user.id)
        if teacher:
            groups = await TeacherRepository.get_teacher_groups(teacher.id)
        else:
            logger.info(f"Пользователь {user.name} не является учителем")

    if not groups:
        await callback.message.edit_text(
            "❌ У вас нет назначенных групп",
            reply_markup=get_back_kb()
        )
        return

    await callback.message.edit_text(
        "Выберите группу для просмотра статистики контрольного теста месяца:",
        reply_markup=await get_curator_groups_kb("month_control", groups)
    )

@router.callback_query(F.data.startswith("month_control_group_"))
async def show_month_control_months(callback: CallbackQuery, state: FSMContext):
    """Показать месяцы для контрольного теста месяца"""
    current_state = await state.get_state()
    logger.info(f"ВЫЗОВ: show_month_control_months, user_id={callback.from_user.id}, текущее состояние={current_state}, callback_data={callback.data}")

    try:
        group_id = int(await check_if_id_in_callback_data("month_control_group_", callback, state, "group_id"))
        await show_month_control_test_months(callback, state, group_id)
    except ValueError:
        await callback.message.edit_text(
            "❌ Ошибка: неверный ID группы",
            reply_markup=get_back_kb()
        )

@router.callback_query(F.data.startswith("back_to_month_control_groups"))
async def back_to_month_control_groups(callback: CallbackQuery, state: FSMContext):
    """Вернуться к выбору группы для контрольного теста месяца"""
    current_state = await state.get_state()
    logger.info(f"ВЫЗОВ: back_to_month_control_groups, user_id={callback.from_user.id}, текущее состояние={current_state}, callback_data={callback.data}")
    await show_month_control_groups(callback, state)

@router.callback_query(F.data.startswith("month_control_month_"))
async def show_month_control_statistics(callback: CallbackQuery, state: FSMContext):
    """Показать статистику контрольного теста месяца"""
    current_state = await state.get_state()
    logger.info(f"ВЫЗОВ: show_month_control_statistics, user_id={callback.from_user.id}, текущее состояние={current_state}, callback_data={callback.data}")

    try:
        # Формат: month_control_month_GROUP_ID_MONTH_TEST_ID
        parts = callback.data.split("_")
        group_id = int(parts[3])
        month_test_id = int(parts[4])
        await show_month_control_test_statistics(callback, state, group_id, month_test_id)
    except (ValueError, IndexError):
        await callback.message.edit_text(
            "❌ Ошибка: неверные параметры",
            reply_markup=get_back_kb()
        )

@router.callback_query(F.data.startswith("compare_tests_"))
async def show_tests_comparison(callback: CallbackQuery, state: FSMContext):
    """Показать сравнение входного и контрольного тестов"""
    current_state = await state.get_state()
    logger.info(f"ВЫЗОВ: show_tests_comparison, user_id={callback.from_user.id}, текущее состояние={current_state}, callback_data={callback.data}")
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

# Обработчики для пробного ЕНТ
@router.callback_query(F.data == "stats_ent_test")
async def show_ent_groups(callback: CallbackQuery, state: FSMContext):
    """Показать группы для пробного ЕНТ"""
    current_state = await state.get_state()
    logger.info(f"ВЫЗОВ: show_ent_groups, user_id={callback.from_user.id}, текущее состояние={current_state}, callback_data={callback.data}")

    # Определяем роль пользователя по состоянию
    role = "curator"  # По умолчанию
    if current_state and "Teacher" in current_state:
        role = "teacher"
    elif current_state and "Curator" in current_state:
        role = "curator"

    # Получаем группы в зависимости от роли
    from database import CuratorRepository, TeacherRepository, UserRepository

    user = await UserRepository.get_by_telegram_id(callback.from_user.id)
    if not user:
        await callback.message.edit_text(
            "❌ Пользователь не найден в системе",
            reply_markup=get_back_kb()
        )
        return

    groups = []

    # Проверяем роль и получаем соответствующие группы
    if role == "curator":
        # Получаем профиль куратора по user_id
        curator = await CuratorRepository.get_by_user_id(user.id)
        if curator:
            groups = await CuratorRepository.get_curator_groups(curator.id)
        else:
            logger.info(f"Пользователь {user.name} не является куратором")

    elif role == "teacher":
        # Получаем профиль учителя по user_id
        teacher = await TeacherRepository.get_by_user_id(user.id)
        if teacher:
            groups = await TeacherRepository.get_teacher_groups(teacher.id)
        else:
            logger.info(f"Пользователь {user.name} не является учителем")

    if not groups:
        await callback.message.edit_text(
            "❌ У вас нет назначенных групп",
            reply_markup=get_back_kb()
        )
        return

    await callback.message.edit_text(
        "Выберите группу для просмотра статистики пробного ЕНТ:",
        reply_markup=await get_curator_groups_kb("ent", groups)
    )

@router.callback_query(F.data.startswith("ent_group_"))
async def show_ent_students(callback: CallbackQuery, state: FSMContext):
    """Показать студентов для пробного ЕНТ"""
    current_state = await state.get_state()
    logger.info(f"ВЫЗОВ: show_ent_students, user_id={callback.from_user.id}, текущее состояние={current_state}, callback_data={callback.data}")

    try:
        group_id = int(await check_if_id_in_callback_data("ent_group_", callback, state, "group_id"))
        await show_trial_ent_statistics(callback, state, group_id)
    except ValueError:
        await callback.message.edit_text(
            "❌ Ошибка: неверный ID группы",
            reply_markup=get_back_kb()
        )

@router.callback_query(F.data.startswith("back_to_ent_groups"))
async def back_to_ent_groups(callback: CallbackQuery, state: FSMContext):
    """Вернуться к выбору группы для пробного ЕНТ"""
    current_state = await state.get_state()
    logger.info(f"ВЫЗОВ: back_to_ent_groups, user_id={callback.from_user.id}, текущее состояние={current_state}, callback_data={callback.data}")
    await show_ent_groups(callback, state)

@router.callback_query(F.data.startswith("ent_student_"))
async def show_ent_statistics(callback: CallbackQuery, state: FSMContext):
    """Показать статистику пробного ЕНТ для студента"""
    current_state = await state.get_state()
    logger.info(f"ВЫЗОВ: show_ent_statistics, user_id={callback.from_user.id}, текущее состояние={current_state}, callback_data={callback.data}")

    try:
        # Формат: ent_student_GROUP_ID_STUDENT_ID
        parts = callback.data.split("_")
        group_id = int(parts[2])
        student_id = int(parts[3])
        await show_trial_ent_student_detail(callback, state, group_id, student_id)
    except (ValueError, IndexError):
        await callback.message.edit_text(
            "❌ Ошибка: неверные параметры",
            reply_markup=get_back_kb()
        )

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
    current_state = await state.get_state()
    logger.info(f"ВЫЗОВ: show_student_test_statistics, user_id={callback.from_user.id}, текущее состояние={current_state}, test_type={test_type}, student_id={student_id}, group_id={group_id}, month_id={month_id}")
    
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

    # Получаем результаты теста из общего компонента
    from common.statistics import get_test_results
    test_results = get_test_results(test_id, student_id)

    # Форматируем результаты теста
    from common.statistics import format_test_result
    result_text = format_test_result(
        test_results, 
        subject_name=subject_name, 
        test_type=test_type,
        month=month_id
    )

    # Добавляем информацию о группе
    group_name = group_id.replace("_", " ").title() if group_id else "Неизвестная группа"
    result_text = result_text.replace("курса пройден", f"{group_name} курса пройден")
    
    from common.tests_statistics.keyboards import get_back_kb
    await callback.message.edit_text(
        result_text,
        reply_markup=get_back_kb()
    )

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
    current_state = await state.get_state()
    logger.info(f"ВЫЗОВ: show_test_students_statistics, user_id={callback.from_user.id}, текущее состояние={current_state}, test_type={test_type}, group_id={group_id}, month_id={month_id}, title={title}")
    
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

async def get_group_id_from_callback_or_state(callback: CallbackQuery, state: FSMContext, prefix: str) -> str:
    """
    Получает ID группы из callback_data или из состояния, если callback_data не содержит ID

    Args:
        callback: Объект CallbackQuery
        state: Контекст состояния FSM
        prefix: Префикс, который нужно удалить из callback_data для получения ID группы

    Returns:
        str: ID группы
    """
    logger.info("get_group_id_from_callback_or_state вызвана с параметрами: callback.data=%s, prefix=%s", 
                callback.data, prefix)
    
    if callback.data.replace(prefix, ""):
        group_id = callback.data.replace(prefix, "")
        logger.info("group_id из callback: %s", group_id)
        await state.update_data(selected_group=group_id)
    else:
        # Если это кнопка "назад" или другой callback, берем ID группы из состояния
        user_data = await state.get_data()
        group_id = user_data.get("selected_group")
        logger.info("group_id из состояния: %s", group_id)

    return group_id





async def show_course_entry_test_statistics(callback: CallbackQuery, state: FSMContext, group_id: int):
    """Показать статистику входного теста курса для группы"""
    from database import CourseEntryTestResultRepository, GroupRepository

    try:
        # Получаем группу
        group = await GroupRepository.get_by_id(group_id)
        if not group:
            await callback.message.edit_text(
                "❌ Группа не найдена",
                reply_markup=get_back_kb()
            )
            return

        # Получаем статистику по группе
        stats = await CourseEntryTestResultRepository.get_statistics_by_group(group_id)

        # Формируем текст сообщения
        result_text = f"📊 Статистика входного теста курса\n\n"
        result_text += f"📗 {stats['subject_name']}\n"
        result_text += f"Группа: {stats['group_name']}\n\n"

        # Показываем прошедших тест
        result_text += "✅ Прошли тест:\n"
        if stats['completed']:
            for i, student in enumerate(stats['completed'], 1):
                # Находим результат теста для этого студента
                test_result = next((tr for tr in stats['test_results'] if tr.student.id == student.id), None)
                percentage = f" ({test_result.score_percentage}%)" if test_result else ""
                result_text += f"{i}. {student.user.name}{percentage}\n"
        else:
            result_text += "Пока никто не прошел тест\n"

        result_text += "\n❌ Не прошли тест:\n"
        if stats['not_completed']:
            for i, student in enumerate(stats['not_completed'], 1):
                result_text += f"{i}. {student.user.name}\n"
        else:
            result_text += "Все студенты прошли тест\n"

        # Добавляем кнопки для просмотра детальной статистики по ученикам
        buttons = []
        for test_result in stats.get('test_results', []):
            student = test_result.student
            buttons.append([
                InlineKeyboardButton(
                    text=f"📊 {student.user.name} ({test_result.score_percentage}%)",
                    callback_data=f"course_entry_student_{group_id}_{student.id}"
                )
            ])

        buttons.extend(get_main_menu_back_button())

        await callback.message.edit_text(
            result_text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
        )

    except Exception as e:
        logger.error(f"Ошибка при получении статистики входного теста курса: {e}")
        await callback.message.edit_text(
            "❌ Ошибка при получении статистики",
            reply_markup=get_back_kb()
        )


async def show_course_entry_student_detail(callback: CallbackQuery, state: FSMContext, group_id: int, student_id: int):
    """Показать детальную статистику входного теста курса для студента"""
    from database import CourseEntryTestResultRepository, StudentRepository, GroupRepository, MicrotopicRepository

    try:
        # Получаем студента
        student = await StudentRepository.get_by_id(student_id)
        if not student:
            await callback.message.edit_text(
                "❌ Студент не найден",
                reply_markup=get_back_kb()
            )
            return

        # Получаем группу
        group = await GroupRepository.get_by_id(group_id)
        if not group:
            await callback.message.edit_text(
                "❌ Группа не найдена",
                reply_markup=get_back_kb()
            )
            return

        # Получаем результат теста студента по предмету группы
        test_result = await CourseEntryTestResultRepository.get_by_student_and_subject(
            student_id, group.subject_id
        )

        if not test_result:
            await callback.message.edit_text(
                f"❌ {student.user.name} еще не проходил входной тест курса по предмету {group.subject.name}",
                reply_markup=get_back_kb()
            )
            return

        # Получаем статистику по микротемам
        microtopic_stats = await CourseEntryTestResultRepository.get_microtopic_statistics(test_result.id)

        # Получаем названия микротем
        microtopics = await MicrotopicRepository.get_by_subject(group.subject_id)
        microtopic_names = {mt.number: mt.name for mt in microtopics}

        # Формируем краткую информацию
        result_text = f"📊 Результат входного теста курса\n\n"
        result_text += f"📗 {group.subject.name}:\n"
        result_text += f"Верных: {test_result.correct_answers} / {test_result.total_questions}\n\n"
        result_text += "Выберите тип аналитики:"

        # Создаем кнопки для детальной аналитики
        from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
        buttons = [
            [InlineKeyboardButton(
                text="📊 Проценты по микротемам",
                callback_data=f"course_entry_detailed_{group_id}_{student_id}"
            )],
            [InlineKeyboardButton(
                text="💪 Сильные/слабые темы",
                callback_data=f"course_entry_summary_{group_id}_{student_id}"
            )]
        ]
        buttons.extend(get_main_menu_back_button())

        await callback.message.edit_text(
            result_text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
        )

    except Exception as e:
        logger.error(f"Ошибка при получении детальной статистики студента: {e}")
        await callback.message.edit_text(
            "❌ Ошибка при получении статистики студента",
            reply_markup=get_back_kb()
        )


# Функции для обработчиков (вызываются из register_handlers.py)
async def show_course_entry_detailed_microtopics(callback: CallbackQuery, state: FSMContext):
    """Показать детальную статистику по микротемам входного теста курса"""
    current_state = await state.get_state()
    logger.info(f"ВЫЗОВ: show_course_entry_detailed_microtopics, user_id={callback.from_user.id}, текущее состояние={current_state}, callback_data={callback.data}")

    try:
        # Формат: course_entry_detailed_GROUP_ID_STUDENT_ID
        parts = callback.data.split("_")
        group_id = int(parts[3])
        student_id = int(parts[4])

        await show_course_entry_microtopics_detailed(callback, state, group_id, student_id)

    except (ValueError, IndexError):
        await callback.message.edit_text(
            "❌ Ошибка: неверные параметры",
            reply_markup=get_back_kb()
        )


async def show_course_entry_summary_microtopics(callback: CallbackQuery, state: FSMContext):
    """Показать сводку по сильным/слабым темам входного теста курса"""
    current_state = await state.get_state()
    logger.info(f"ВЫЗОВ: show_course_entry_summary_microtopics, user_id={callback.from_user.id}, текущее состояние={current_state}, callback_data={callback.data}")

    try:
        # Формат: course_entry_summary_GROUP_ID_STUDENT_ID
        parts = callback.data.split("_")
        group_id = int(parts[3])
        student_id = int(parts[4])

        await show_course_entry_microtopics_summary(callback, state, group_id, student_id)

    except (ValueError, IndexError):
        await callback.message.edit_text(
            "❌ Ошибка: неверные параметры",
            reply_markup=get_back_kb()
        )


async def show_course_entry_microtopics_detailed(callback: CallbackQuery, state: FSMContext, group_id: int, student_id: int):
    """Показать детальную статистику по микротемам входного теста курса"""
    from database import CourseEntryTestResultRepository, StudentRepository, GroupRepository, MicrotopicRepository

    try:
        # Получаем студента и группу
        student = await StudentRepository.get_by_id(student_id)
        group = await GroupRepository.get_by_id(group_id)

        if not student or not group:
            await callback.message.edit_text(
                "❌ Студент или группа не найдены",
                reply_markup=get_back_kb()
            )
            return

        # Получаем результат теста
        test_result = await CourseEntryTestResultRepository.get_by_student_and_subject(
            student_id, group.subject_id
        )

        if not test_result:
            await callback.message.edit_text(
                f"❌ {student.user.name} еще не проходил входной тест курса по предмету {group.subject.name}",
                reply_markup=get_back_kb()
            )
            return

        # Получаем статистику по микротемам
        microtopic_stats = await CourseEntryTestResultRepository.get_microtopic_statistics(test_result.id)

        # Получаем названия микротем
        microtopics = await MicrotopicRepository.get_by_subject(group.subject_id)
        microtopic_names = {mt.number: mt.name for mt in microtopics}

        # Формируем детальную статистику
        result_text = f"📊 Детальная статистика входного теста курса\n\n"
        result_text += f"👤 {student.user.name}\n"
        result_text += f"📗 {group.subject.name}:\n"
        result_text += f"Верных: {test_result.correct_answers} / {test_result.total_questions}\n\n"
        result_text += "📈 % правильных ответов по микротемам:\n"

        if microtopic_stats:
            for microtopic_num in sorted(microtopic_stats.keys()):
                stats = microtopic_stats[microtopic_num]
                microtopic_name = microtopic_names.get(microtopic_num, f"Микротема {microtopic_num}")
                percentage = stats['percentage']

                # Определяем эмодзи статуса
                if percentage >= 80:
                    status = "✅"
                elif percentage <= 40:
                    status = "❌"
                else:
                    status = "⚠️"

                result_text += f"• {microtopic_name} — {percentage}% {status}\n"
        else:
            result_text += "Нет данных по микротемам\n"

        await callback.message.edit_text(
            result_text,
            reply_markup=get_back_kb()
        )

    except Exception as e:
        logger.error(f"Ошибка при получении детальной статистики входного теста: {e}")
        await callback.message.edit_text(
            "❌ Ошибка при получении статистики",
            reply_markup=get_back_kb()
        )


async def show_course_entry_microtopics_summary(callback: CallbackQuery, state: FSMContext, group_id: int, student_id: int):
    """Показать сводку по сильным/слабым темам входного теста курса"""
    from database import CourseEntryTestResultRepository, StudentRepository, GroupRepository, MicrotopicRepository

    try:
        # Получаем студента и группу
        student = await StudentRepository.get_by_id(student_id)
        group = await GroupRepository.get_by_id(group_id)

        if not student or not group:
            await callback.message.edit_text(
                "❌ Студент или группа не найдены",
                reply_markup=get_back_kb()
            )
            return

        # Получаем результат теста
        test_result = await CourseEntryTestResultRepository.get_by_student_and_subject(
            student_id, group.subject_id
        )

        if not test_result:
            await callback.message.edit_text(
                f"❌ {student.user.name} еще не проходил входной тест курса по предмету {group.subject.name}",
                reply_markup=get_back_kb()
            )
            return

        # Получаем статистику по микротемам
        microtopic_stats = await CourseEntryTestResultRepository.get_microtopic_statistics(test_result.id)

        # Получаем названия микротем
        microtopics = await MicrotopicRepository.get_by_subject(group.subject_id)
        microtopic_names = {mt.number: mt.name for mt in microtopics}

        # Определяем сильные и слабые темы
        strong_topics = []
        weak_topics = []

        for microtopic_num, stats in microtopic_stats.items():
            microtopic_name = microtopic_names.get(microtopic_num, f"Микротема {microtopic_num}")
            percentage = stats['percentage']

            if percentage >= 80:
                strong_topics.append(microtopic_name)
            elif percentage <= 40:
                weak_topics.append(microtopic_name)

        # Формируем сводку
        result_text = f"💪 Сводка по входному тесту курса\n\n"
        result_text += f"👤 {student.user.name}\n"
        result_text += f"📗 {group.subject.name}:\n"
        result_text += f"Верных: {test_result.correct_answers} / {test_result.total_questions}\n\n"

        if strong_topics:
            result_text += "🟢 Сильные темы (≥80%):\n"
            for topic in strong_topics:
                result_text += f"• {topic}\n"

        if weak_topics:
            if strong_topics:
                result_text += "\n"
            result_text += "🔴 Слабые темы (≤40%):\n"
            for topic in weak_topics:
                result_text += f"• {topic}\n"

        if not strong_topics and not weak_topics:
            result_text += "⚠️ Все темы находятся в среднем диапазоне (41-79%)"

        await callback.message.edit_text(
            result_text,
            reply_markup=get_back_kb()
        )

    except Exception as e:
        logger.error(f"Ошибка при получении сводки входного теста: {e}")
        await callback.message.edit_text(
            "❌ Ошибка при получении сводки",
            reply_markup=get_back_kb()
        )


# Функции для входного теста месяца
async def show_month_entry_test_months(callback: CallbackQuery, state: FSMContext, group_id: int):
    """Показать доступные тесты месяца для группы"""
    from database import GroupRepository, MonthTestRepository
    from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

    try:
        # Получаем группу
        group = await GroupRepository.get_by_id(group_id)
        if not group:
            await callback.message.edit_text(
                "❌ Группа не найдена",
                reply_markup=get_back_kb()
            )
            return

        # Получаем все тесты месяца для предмета группы
        all_month_tests = await MonthTestRepository.get_all()
        group_month_tests = [mt for mt in all_month_tests if mt.subject_id == group.subject_id]

        if not group_month_tests:
            await callback.message.edit_text(
                f"❌ Для предмета {group.subject.name} пока нет созданных тестов месяца",
                reply_markup=get_back_kb()
            )
            return

        # Создаем кнопки для каждого теста месяца
        buttons = []
        for month_test in group_month_tests:
            buttons.append([
                InlineKeyboardButton(
                    text=month_test.name,
                    callback_data=f"month_entry_month_{group_id}_{month_test.id}"
                )
            ])

        buttons.extend(get_main_menu_back_button())

        await callback.message.edit_text(
            f"Выберите тест месяца для просмотра статистики:\n\n📗 {group.subject.name}\nГруппа: {group.name}",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
        )

    except Exception as e:
        logger.error(f"Ошибка при получении тестов месяца: {e}")
        await callback.message.edit_text(
            "❌ Ошибка при получении тестов месяца",
            reply_markup=get_back_kb()
        )


async def show_month_entry_test_statistics(callback: CallbackQuery, state: FSMContext, group_id: int, month_test_id: int):
    """Показать статистику входного теста месяца для группы"""
    from database import MonthEntryTestResultRepository, GroupRepository, MonthTestRepository

    try:
        # Получаем группу и тест месяца
        group = await GroupRepository.get_by_id(group_id)
        month_test = await MonthTestRepository.get_by_id(month_test_id)

        if not group or not month_test:
            await callback.message.edit_text(
                "❌ Группа или тест месяца не найдены",
                reply_markup=get_back_kb()
            )
            return

        # Получаем статистику по группе и тесту месяца
        stats = await MonthEntryTestResultRepository.get_statistics_by_group_and_month_test(group_id, month_test_id)

        # Формируем текст сообщения
        result_text = f"📊 Статистика входного теста месяца\n\n"
        result_text += f"📗 {stats['subject_name']}\n"
        result_text += f"Группа: {stats['group_name']}\n"
        result_text += f"Тест: {stats['month_test_name']}\n\n"

        # Показываем прошедших тест
        result_text += "✅ Прошли тест:\n"
        if stats['completed']:
            for i, student in enumerate(stats['completed'], 1):
                # Находим результат теста для этого студента
                test_result = next((tr for tr in stats['test_results'] if tr.student.id == student.id), None)
                percentage = f" ({test_result.score_percentage}%)" if test_result else ""
                result_text += f"{i}. {student.user.name}{percentage}\n"
        else:
            result_text += "Пока никто не прошел тест\n"

        result_text += "\n❌ Не прошли тест:\n"
        if stats['not_completed']:
            for i, student in enumerate(stats['not_completed'], 1):
                result_text += f"{i}. {student.user.name}\n"
        else:
            result_text += "Все студенты прошли тест\n"

        # Добавляем кнопки для просмотра детальной статистики по ученикам
        buttons = []
        for test_result in stats.get('test_results', []):
            student = test_result.student
            buttons.append([
                InlineKeyboardButton(
                    text=f"📊 {student.user.name} ({test_result.score_percentage}%)",
                    callback_data=f"month_entry_student_{group_id}_{month_test_id}_{student.id}"
                )
            ])

        buttons.extend(get_main_menu_back_button())

        await callback.message.edit_text(
            result_text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
        )

    except Exception as e:
        logger.error(f"Ошибка при получении статистики входного теста месяца: {e}")
        await callback.message.edit_text(
            "❌ Ошибка при получении статистики",
            reply_markup=get_back_kb()
        )


async def show_month_entry_student_detail(callback: CallbackQuery, state: FSMContext, group_id: int, month_test_id: int, student_id: int):
    """Показать детальную статистику входного теста месяца для студента"""
    from database import MonthEntryTestResultRepository, StudentRepository, GroupRepository, MonthTestRepository, MicrotopicRepository

    try:
        # Получаем студента, группу и тест месяца
        student = await StudentRepository.get_by_id(student_id)
        group = await GroupRepository.get_by_id(group_id)
        month_test = await MonthTestRepository.get_by_id(month_test_id)

        if not student or not group or not month_test:
            await callback.message.edit_text(
                "❌ Студент, группа или тест месяца не найдены",
                reply_markup=get_back_kb()
            )
            return

        # Получаем результат теста студента
        test_result = await MonthEntryTestResultRepository.get_by_student_and_month_test(
            student_id, month_test_id
        )

        if not test_result:
            await callback.message.edit_text(
                f"❌ {student.user.name} еще не проходил входной тест месяца '{month_test.name}'",
                reply_markup=get_back_kb()
            )
            return

        # Получаем статистику по микротемам
        microtopic_stats = await MonthEntryTestResultRepository.get_microtopic_statistics(test_result.id)

        # Получаем названия микротем
        microtopics = await MicrotopicRepository.get_by_subject(group.subject_id)
        microtopic_names = {mt.number: mt.name for mt in microtopics}

        # Формируем краткую информацию
        result_text = f"📊 Результат входного теста месяца\n\n"
        result_text += f"📗 {group.subject.name}:\n"
        result_text += f"Тест: {month_test.name}\n"
        result_text += f"Верных: {test_result.correct_answers} / {test_result.total_questions}\n\n"
        result_text += "Выберите тип аналитики:"

        # Создаем кнопки для детальной аналитики
        from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
        buttons = [
            [InlineKeyboardButton(
                text="📊 Проценты по микротемам",
                callback_data=f"month_entry_detailed_{group_id}_{month_test_id}_{student_id}"
            )],
            [InlineKeyboardButton(
                text="💪 Сильные/слабые темы",
                callback_data=f"month_entry_summary_{group_id}_{month_test_id}_{student_id}"
            )]
        ]
        buttons.extend(get_main_menu_back_button())

        await callback.message.edit_text(
            result_text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
        )

    except Exception as e:
        logger.error(f"Ошибка при получении детальной статистики студента: {e}")
        await callback.message.edit_text(
            "❌ Ошибка при получении статистики студента",
            reply_markup=get_back_kb()
        )


# Функции для обработчиков детальной аналитики входного теста месяца (вызываются из register_handlers.py)
async def show_month_entry_detailed_microtopics(callback: CallbackQuery, state: FSMContext):
    """Показать детальную статистику по микротемам входного теста месяца"""
    current_state = await state.get_state()
    logger.info(f"ВЫЗОВ: show_month_entry_detailed_microtopics, user_id={callback.from_user.id}, текущее состояние={current_state}, callback_data={callback.data}")

    try:
        # Формат: month_entry_detailed_GROUP_ID_MONTH_TEST_ID_STUDENT_ID
        parts = callback.data.split("_")
        group_id = int(parts[3])
        month_test_id = int(parts[4])
        student_id = int(parts[5])

        await show_month_entry_microtopics_detailed(callback, state, group_id, month_test_id, student_id)

    except (ValueError, IndexError):
        await callback.message.edit_text(
            "❌ Ошибка: неверные параметры",
            reply_markup=get_back_kb()
        )


async def show_month_entry_summary_microtopics(callback: CallbackQuery, state: FSMContext):
    """Показать сводку по сильным/слабым темам входного теста месяца"""
    current_state = await state.get_state()
    logger.info(f"ВЫЗОВ: show_month_entry_summary_microtopics, user_id={callback.from_user.id}, текущее состояние={current_state}, callback_data={callback.data}")

    try:
        # Формат: month_entry_summary_GROUP_ID_MONTH_TEST_ID_STUDENT_ID
        parts = callback.data.split("_")
        group_id = int(parts[3])
        month_test_id = int(parts[4])
        student_id = int(parts[5])

        await show_month_entry_microtopics_summary(callback, state, group_id, month_test_id, student_id)

    except (ValueError, IndexError):
        await callback.message.edit_text(
            "❌ Ошибка: неверные параметры",
            reply_markup=get_back_kb()
        )


async def show_month_entry_microtopics_detailed(callback: CallbackQuery, state: FSMContext, group_id: int, month_test_id: int, student_id: int):
    """Показать детальную статистику по микротемам входного теста месяца"""
    from database import MonthEntryTestResultRepository, StudentRepository, GroupRepository, MonthTestRepository, MicrotopicRepository

    try:
        # Получаем студента, группу и тест месяца
        student = await StudentRepository.get_by_id(student_id)
        group = await GroupRepository.get_by_id(group_id)
        month_test = await MonthTestRepository.get_by_id(month_test_id)

        if not student or not group or not month_test:
            await callback.message.edit_text(
                "❌ Студент, группа или тест месяца не найдены",
                reply_markup=get_back_kb()
            )
            return

        # Получаем результат теста
        test_result = await MonthEntryTestResultRepository.get_by_student_and_month_test(
            student_id, month_test_id
        )

        if not test_result:
            await callback.message.edit_text(
                f"❌ {student.user.name} еще не проходил входной тест месяца '{month_test.name}'",
                reply_markup=get_back_kb()
            )
            return

        # Получаем статистику по микротемам
        microtopic_stats = await MonthEntryTestResultRepository.get_microtopic_statistics(test_result.id)

        # Получаем названия микротем
        microtopics = await MicrotopicRepository.get_by_subject(group.subject_id)
        microtopic_names = {mt.number: mt.name for mt in microtopics}

        # Формируем детальную статистику
        result_text = f"📊 Детальная статистика входного теста месяца\n\n"
        result_text += f"👤 {student.user.name}\n"
        result_text += f"📗 {group.subject.name}:\n"
        result_text += f"Тест: {month_test.name}\n"
        result_text += f"Верных: {test_result.correct_answers} / {test_result.total_questions}\n\n"
        result_text += "📈 % правильных ответов по микротемам:\n"

        if microtopic_stats:
            for microtopic_num in sorted(microtopic_stats.keys()):
                stats = microtopic_stats[microtopic_num]
                microtopic_name = microtopic_names.get(microtopic_num, f"Микротема {microtopic_num}")
                percentage = stats['percentage']

                # Определяем эмодзи статуса
                if percentage >= 80:
                    status = "✅"
                elif percentage <= 40:
                    status = "❌"
                else:
                    status = "⚠️"

                result_text += f"• {microtopic_name} — {percentage}% {status}\n"
        else:
            result_text += "Нет данных по микротемам\n"

        await callback.message.edit_text(
            result_text,
            reply_markup=get_back_kb()
        )

    except Exception as e:
        logger.error(f"Ошибка при получении детальной статистики входного теста месяца: {e}")
        await callback.message.edit_text(
            "❌ Ошибка при получении статистики",
            reply_markup=get_back_kb()
        )


async def show_month_entry_microtopics_summary(callback: CallbackQuery, state: FSMContext, group_id: int, month_test_id: int, student_id: int):
    """Показать сводку по сильным/слабым темам входного теста месяца"""
    from database import MonthEntryTestResultRepository, StudentRepository, GroupRepository, MonthTestRepository, MicrotopicRepository

    try:
        # Получаем студента, группу и тест месяца
        student = await StudentRepository.get_by_id(student_id)
        group = await GroupRepository.get_by_id(group_id)
        month_test = await MonthTestRepository.get_by_id(month_test_id)

        if not student or not group or not month_test:
            await callback.message.edit_text(
                "❌ Студент, группа или тест месяца не найдены",
                reply_markup=get_back_kb()
            )
            return

        # Получаем результат теста
        test_result = await MonthEntryTestResultRepository.get_by_student_and_month_test(
            student_id, month_test_id
        )

        if not test_result:
            await callback.message.edit_text(
                f"❌ {student.user.name} еще не проходил входной тест месяца '{month_test.name}'",
                reply_markup=get_back_kb()
            )
            return

        # Получаем статистику по микротемам
        microtopic_stats = await MonthEntryTestResultRepository.get_microtopic_statistics(test_result.id)

        # Получаем названия микротем
        microtopics = await MicrotopicRepository.get_by_subject(group.subject_id)
        microtopic_names = {mt.number: mt.name for mt in microtopics}

        # Определяем сильные и слабые темы
        strong_topics = []
        weak_topics = []

        for microtopic_num, stats in microtopic_stats.items():
            microtopic_name = microtopic_names.get(microtopic_num, f"Микротема {microtopic_num}")
            percentage = stats['percentage']

            if percentage >= 80:
                strong_topics.append(microtopic_name)
            elif percentage <= 40:
                weak_topics.append(microtopic_name)

        # Формируем сводку
        result_text = f"💪 Сводка по входному тесту месяца\n\n"
        result_text += f"👤 {student.user.name}\n"
        result_text += f"📗 {group.subject.name}:\n"
        result_text += f"Тест: {month_test.name}\n"
        result_text += f"Верных: {test_result.correct_answers} / {test_result.total_questions}\n\n"

        if strong_topics:
            result_text += "🟢 Сильные темы (≥80%):\n"
            for topic in strong_topics:
                result_text += f"• {topic}\n"

        if weak_topics:
            if strong_topics:
                result_text += "\n"
            result_text += "🔴 Слабые темы (≤40%):\n"
            for topic in weak_topics:
                result_text += f"• {topic}\n"

        if not strong_topics and not weak_topics:
            result_text += "⚠️ Все темы находятся в среднем диапазоне (41-79%)"

        await callback.message.edit_text(
            result_text,
            reply_markup=get_back_kb()
        )

    except Exception as e:
        logger.error(f"Ошибка при получении сводки входного теста месяца: {e}")
        await callback.message.edit_text(
            "❌ Ошибка при получении сводки",
            reply_markup=get_back_kb()
        )


async def show_month_entry_microtopics_summary(callback: CallbackQuery, state: FSMContext, group_id: int, month_test_id: int, student_id: int):
    """Показать сводку по сильным/слабым темам входного теста месяца"""
    from database import MonthEntryTestResultRepository, StudentRepository, GroupRepository, MonthTestRepository, MicrotopicRepository

    try:
        # Получаем студента, группу и тест месяца
        student = await StudentRepository.get_by_id(student_id)
        group = await GroupRepository.get_by_id(group_id)
        month_test = await MonthTestRepository.get_by_id(month_test_id)

        if not student or not group or not month_test:
            await callback.message.edit_text(
                "❌ Студент, группа или тест месяца не найдены",
                reply_markup=get_back_kb()
            )
            return

        # Получаем результат теста
        test_result = await MonthEntryTestResultRepository.get_by_student_and_month_test(
            student_id, month_test_id
        )

        if not test_result:
            await callback.message.edit_text(
                f"❌ {student.user.name} еще не проходил входной тест месяца '{month_test.name}'",
                reply_markup=get_back_kb()
            )
            return

        # Получаем статистику по микротемам
        microtopic_stats = await MonthEntryTestResultRepository.get_microtopic_statistics(test_result.id)

        # Получаем названия микротем
        microtopics = await MicrotopicRepository.get_by_subject(group.subject_id)
        microtopic_names = {mt.number: mt.name for mt in microtopics}

        # Определяем сильные и слабые темы
        strong_topics = []
        weak_topics = []

        for microtopic_num, stats in microtopic_stats.items():
            microtopic_name = microtopic_names.get(microtopic_num, f"Микротема {microtopic_num}")
            percentage = stats['percentage']

            if percentage >= 80:
                strong_topics.append(microtopic_name)
            elif percentage <= 40:
                weak_topics.append(microtopic_name)

        # Формируем сводку
        result_text = f"💪 Сводка по входному тесту месяца\n\n"
        result_text += f"👤 {student.user.name}\n"
        result_text += f"📗 {group.subject.name}:\n"
        result_text += f"Тест: {month_test.name}\n"
        result_text += f"Верных: {test_result.correct_answers} / {test_result.total_questions}\n\n"

        if strong_topics:
            result_text += "🟢 Сильные темы (≥80%):\n"
            for topic in strong_topics:
                result_text += f"• {topic}\n"

        if weak_topics:
            if strong_topics:
                result_text += "\n"
            result_text += "🔴 Слабые темы (≤40%):\n"
            for topic in weak_topics:
                result_text += f"• {topic}\n"

        if not strong_topics and not weak_topics:
            result_text += "⚠️ Все темы находятся в среднем диапазоне (41-79%)"

        await callback.message.edit_text(
            result_text,
            reply_markup=get_back_kb()
        )

    except Exception as e:
        logger.error(f"Ошибка при получении сводки входного теста месяца: {e}")
        await callback.message.edit_text(
            "❌ Ошибка при получении сводки",
            reply_markup=get_back_kb()
        )


# Функции для пробного ЕНТ
async def show_trial_ent_statistics(callback: CallbackQuery, state: FSMContext, group_id: int):
    """Показать статистику пробного ЕНТ для группы"""
    from database import TrialEntResultRepository, GroupRepository
    from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

    try:
        # Получаем группу
        group = await GroupRepository.get_by_id(group_id)
        if not group:
            await callback.message.edit_text(
                "❌ Группа не найдена",
                reply_markup=get_back_kb()
            )
            return

        # Получаем статистику по группе
        stats = await TrialEntResultRepository.get_statistics_by_group(group_id)

        # Формируем текст сообщения
        result_text = f"📊 Статистика пробного ЕНТ\n\n"
        result_text += f"Группа: {stats['group_name']}\n\n"

        # Показываем прошедших тест
        result_text += "✅ Проходили тест:\n"
        if stats['completed']:
            for i, student in enumerate(stats['completed'], 1):
                # Находим последний результат теста для этого студента
                latest_result = next((tr for tr in stats['test_results'] if tr.student.id == student.id), None)
                if latest_result:
                    percentage = round((latest_result.correct_answers / latest_result.total_questions) * 100) if latest_result.total_questions > 0 else 0
                    result_text += f"{i}. {student.user.name} ({percentage}%)\n"
                else:
                    result_text += f"{i}. {student.user.name}\n"
        else:
            result_text += "Пока никто не проходил тест\n"

        result_text += "\n❌ Не проходили тест:\n"
        if stats['not_completed']:
            for i, student in enumerate(stats['not_completed'], 1):
                result_text += f"{i}. {student.user.name}\n"
        else:
            result_text += "Все студенты проходили тест\n"

        # Добавляем кнопки для просмотра детальной статистики по ученикам
        buttons = []
        for test_result in stats.get('test_results', []):
            student = test_result.student
            percentage = round((test_result.correct_answers / test_result.total_questions) * 100) if test_result.total_questions > 0 else 0
            buttons.append([
                InlineKeyboardButton(
                    text=f"📊 {student.user.name} ({percentage}%)",
                    callback_data=f"ent_student_{group_id}_{student.id}"
                )
            ])

        buttons.extend(get_main_menu_back_button())

        await callback.message.edit_text(
            result_text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
        )

    except Exception as e:
        logger.error(f"Ошибка при получении статистики пробного ЕНТ: {e}")
        await callback.message.edit_text(
            "❌ Ошибка при получении статистики",
            reply_markup=get_back_kb()
        )


async def show_trial_ent_student_detail(callback: CallbackQuery, state: FSMContext, group_id: int, student_id: int):
    """Показать детальную статистику пробного ЕНТ для студента"""
    from database import TrialEntResultRepository, StudentRepository, GroupRepository
    from common.trial_ent_service import TrialEntService
    import json

    try:
        # Получаем студента
        student = await StudentRepository.get_by_id(student_id)
        if not student:
            await callback.message.edit_text(
                "❌ Студент не найден",
                reply_markup=get_back_kb()
            )
            return

        # Получаем группу
        group = await GroupRepository.get_by_id(group_id)
        if not group:
            await callback.message.edit_text(
                "❌ Группа не найдена",
                reply_markup=get_back_kb()
            )
            return

        # Получаем последний результат пробного ЕНТ студента
        latest_result = await TrialEntResultRepository.get_latest_by_student(student_id)

        if not latest_result:
            await callback.message.edit_text(
                f"❌ {student.user.name} еще не проходил пробный ЕНТ",
                reply_markup=get_back_kb()
            )
            return

        # Получаем статистику
        statistics = await TrialEntService.get_trial_ent_statistics(latest_result.id)

        # Парсим выбранные предметы
        required_subjects = json.loads(latest_result.required_subjects)
        profile_subjects = json.loads(latest_result.profile_subjects)

        # Формируем краткую информацию
        result_text = f"📊 Результат пробного ЕНТ\n\n"
        result_text += f"👤 {student.user.name}\n"
        result_text += f"Группа: {group.name}\n"
        result_text += f"Верных: {latest_result.correct_answers} / {latest_result.total_questions}\n"

        # Показываем результаты по предметам
        subject_stats = statistics.get('subject_statistics', {})
        if subject_stats:
            result_text += "\n📈 Результаты по предметам:\n"

            # Обязательные предметы
            for subject_code in required_subjects:
                subject_name = TrialEntService.get_subject_name(subject_code)
                stats = subject_stats.get(subject_code, {})
                if stats:
                    result_text += f"• {subject_name}: {stats['correct']}/{stats['total']} ({stats['percentage']}%)\n"

            # Профильные предметы
            for subject_code in profile_subjects:
                subject_name = TrialEntService.get_subject_name(subject_code)
                stats = subject_stats.get(subject_code, {})
                if stats:
                    result_text += f"• {subject_name}: {stats['correct']}/{stats['total']} ({stats['percentage']}%)\n"

        result_text += f"\nДата прохождения: {latest_result.completed_at.strftime('%d.%m.%Y %H:%M')}"

        await callback.message.edit_text(
            result_text,
            reply_markup=get_back_kb()
        )

    except Exception as e:
        logger.error(f"Ошибка при получении детальной статистики пробного ЕНТ: {e}")
        await callback.message.edit_text(
            "❌ Ошибка при получении статистики студента",
            reply_markup=get_back_kb()
        )


# Функции для контрольного теста месяца
async def show_month_control_test_months(callback: CallbackQuery, state: FSMContext, group_id: int):
    """Показать доступные контрольные тесты месяца для группы"""
    from database import GroupRepository, MonthTestRepository
    from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

    try:
        # Получаем группу
        group = await GroupRepository.get_by_id(group_id)
        if not group:
            await callback.message.edit_text(
                "❌ Группа не найдена",
                reply_markup=get_back_kb()
            )
            return

        # Получаем все тесты месяца для предмета группы
        all_month_tests = await MonthTestRepository.get_all()
        # Фильтруем только контрольные тесты для предмета группы
        group_control_tests = [mt for mt in all_month_tests if mt.subject_id == group.subject_id and mt.test_type == 'control']

        if not group_control_tests:
            await callback.message.edit_text(
                f"❌ Для предмета {group.subject.name} пока нет созданных контрольных тестов месяца",
                reply_markup=get_back_kb()
            )
            return

        # Создаем кнопки для каждого контрольного теста месяца
        buttons = []
        for month_test in group_control_tests:
            buttons.append([
                InlineKeyboardButton(
                    text=month_test.name,
                    callback_data=f"month_control_month_{group_id}_{month_test.id}"
                )
            ])

        buttons.extend(get_main_menu_back_button())

        await callback.message.edit_text(
            f"Выберите контрольный тест месяца для просмотра статистики:\n\n📗 {group.subject.name}\nГруппа: {group.name}",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
        )

    except Exception as e:
        logger.error(f"Ошибка при получении контрольных тестов месяца: {e}")
        await callback.message.edit_text(
            "❌ Ошибка при получении контрольных тестов месяца",
            reply_markup=get_back_kb()
        )


async def show_month_control_test_statistics(callback: CallbackQuery, state: FSMContext, group_id: int, month_test_id: int):
    """Показать статистику контрольного теста месяца для группы"""
    from database import MonthEntryTestResultRepository, GroupRepository, MonthTestRepository

    try:
        # Получаем группу и тест месяца
        group = await GroupRepository.get_by_id(group_id)
        month_test = await MonthTestRepository.get_by_id(month_test_id)

        if not group or not month_test:
            await callback.message.edit_text(
                "❌ Группа или контрольный тест месяца не найдены",
                reply_markup=get_back_kb()
            )
            return

        # Получаем статистику по группе и тесту месяца
        stats = await MonthEntryTestResultRepository.get_statistics_by_group_and_month_test(group_id, month_test_id)

        # Формируем текст сообщения
        result_text = f"📊 Статистика контрольного теста месяца\n\n"
        result_text += f"📗 {stats['subject_name']}\n"
        result_text += f"Группа: {stats['group_name']}\n"
        result_text += f"Тест: {stats['month_test_name']}\n\n"

        # Показываем прошедших тест
        result_text += "✅ Прошли тест:\n"
        if stats['completed']:
            for i, student in enumerate(stats['completed'], 1):
                # Находим результат теста для этого студента
                test_result = next((tr for tr in stats['test_results'] if tr.student.id == student.id), None)
                percentage = f" ({test_result.score_percentage}%)" if test_result else ""
                result_text += f"{i}. {student.user.name}{percentage}\n"
        else:
            result_text += "Пока никто не прошел тест\n"

        result_text += "\n❌ Не прошли тест:\n"
        if stats['not_completed']:
            for i, student in enumerate(stats['not_completed'], 1):
                result_text += f"{i}. {student.user.name}\n"
        else:
            result_text += "Все студенты прошли тест\n"

        # Добавляем кнопки для просмотра детальной статистики по ученикам
        buttons = []
        for test_result in stats.get('test_results', []):
            student = test_result.student
            buttons.append([
                InlineKeyboardButton(
                    text=f"📊 {student.user.name} ({test_result.score_percentage}%)",
                    callback_data=f"month_control_student_{group_id}_{month_test_id}_{student.id}"
                )
            ])

        buttons.extend(get_main_menu_back_button())

        await callback.message.edit_text(
            result_text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
        )

    except Exception as e:
        logger.error(f"Ошибка при получении статистики контрольного теста месяца: {e}")
        await callback.message.edit_text(
            "❌ Ошибка при получении статистики",
            reply_markup=get_back_kb()
        )


# Обработчик для детальной статистики студента по контрольному тесту месяца
async def show_month_control_student_statistics(callback: CallbackQuery, state: FSMContext):
    """Показать статистику контрольного теста месяца для конкретного ученика"""
    current_state = await state.get_state()
    logger.info(f"ВЫЗОВ: show_month_control_student_statistics, user_id={callback.from_user.id}, текущее состояние={current_state}, callback_data={callback.data}")

    try:
        # Формат: month_control_student_GROUP_ID_MONTH_TEST_ID_STUDENT_ID
        parts = callback.data.split("_")
        group_id = int(parts[3])
        month_test_id = int(parts[4])
        student_id = int(parts[5])
        await show_month_control_student_detail(callback, state, group_id, month_test_id, student_id)
    except (ValueError, IndexError):
        await callback.message.edit_text(
            "❌ Ошибка: неверные параметры",
            reply_markup=get_back_kb()
        )


async def show_month_control_student_detail(callback: CallbackQuery, state: FSMContext, group_id: int, month_test_id: int, student_id: int):
    """Показать краткую информацию о контрольном тесте месяца для студента с кратким сравнением"""
    from database import (
        MonthEntryTestResultRepository,
        StudentRepository, GroupRepository, MonthTestRepository
    )

    try:
        # Получаем студента, группу и тест месяца
        student = await StudentRepository.get_by_id(student_id)
        group = await GroupRepository.get_by_id(group_id)
        month_test = await MonthTestRepository.get_by_id(month_test_id)

        if not student or not group or not month_test:
            await callback.message.edit_text(
                "❌ Студент, группа или контрольный тест месяца не найдены",
                reply_markup=get_back_kb()
            )
            return

        # Получаем результат контрольного теста студента
        control_result = await MonthEntryTestResultRepository.get_by_student_and_month_test(
            student_id, month_test_id
        )

        if not control_result:
            await callback.message.edit_text(
                f"❌ {student.user.name} еще не проходил контрольный тест месяца '{month_test.name}'",
                reply_markup=get_back_kb()
            )
            return

        # Формируем краткую информацию
        result_text = f"📊 Результат контрольного теста месяца\n\n"
        result_text += f"👤 {student.user.name}\n"
        result_text += f"📗 {group.subject.name}:\n"
        result_text += f"Тест: {month_test.name}\n"

        # Пытаемся найти соответствующий входной тест для краткого сравнения
        entry_test = None
        if month_test.parent_test_id:
            entry_test = await MonthTestRepository.get_by_id(month_test.parent_test_id)

        if entry_test:
            # Получаем результат входного теста
            entry_result = await MonthEntryTestResultRepository.get_by_student_and_month_test(
                student_id, entry_test.id
            )

            if entry_result:
                # Показываем краткое сравнение
                result_text += f"Верных: {entry_result.correct_answers}/{entry_result.total_questions} → {control_result.correct_answers}/{control_result.total_questions}\n"

                # Рассчитываем общий рост по формуле KPI
                entry_percentage = entry_result.score_percentage
                control_percentage = control_result.score_percentage

                if entry_percentage > 0:
                    growth_percentage = ((control_percentage - entry_percentage) / entry_percentage) * 100
                    if growth_percentage > 0:
                        result_text += f"Общий рост: +{growth_percentage:.1f}%\n"
                    elif growth_percentage < 0:
                        result_text += f"Общий рост: {growth_percentage:.1f}%\n"
                    else:
                        result_text += f"Результат остался на том же уровне\n"
                else:
                    # Если входной тест 0%, показываем абсолютный рост в процентных пунктах
                    if control_percentage > 0:
                        result_text += f"Общий рост: +{control_percentage:.1f} п.п.\n"
                    else:
                        result_text += f"Оба теста показали 0%\n"
            else:
                # Если входной тест не пройден, показываем только контрольный
                result_text += f"Верных: {control_result.correct_answers}/{control_result.total_questions}\n"
        else:
            # Если входной тест не найден, показываем только контрольный
            result_text += f"Верных: {control_result.correct_answers}/{control_result.total_questions}\n"

        result_text += "\nВыберите тип аналитики:"

        # Создаем кнопки для детальной аналитики (убираем кнопку сравнения)
        from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
        buttons = [
            [InlineKeyboardButton(
                text="📊 Проценты по микротемам",
                callback_data=f"month_control_detailed_{group_id}_{month_test_id}_{student_id}"
            )],
            [InlineKeyboardButton(
                text="💪 Сильные/слабые темы",
                callback_data=f"month_control_summary_{group_id}_{month_test_id}_{student_id}"
            )]
        ]
        buttons.extend(get_main_menu_back_button())

        await callback.message.edit_text(
            result_text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
        )

    except Exception as e:
        logger.error(f"Ошибка при получении детальной статистики студента по контрольному тесту: {e}")
        await callback.message.edit_text(
            "❌ Ошибка при получении статистики студента",
            reply_markup=get_back_kb()
        )


# Функции для обработчиков детальной аналитики контрольного теста месяца
async def show_month_control_detailed_microtopics(callback: CallbackQuery, state: FSMContext):
    """Показать детальную статистику по микротемам контрольного теста месяца"""
    current_state = await state.get_state()
    logger.info(f"ВЫЗОВ: show_month_control_detailed_microtopics, user_id={callback.from_user.id}, текущее состояние={current_state}, callback_data={callback.data}")

    try:
        # Формат: month_control_detailed_GROUP_ID_MONTH_TEST_ID_STUDENT_ID
        parts = callback.data.split("_")
        group_id = int(parts[3])
        month_test_id = int(parts[4])
        student_id = int(parts[5])

        await show_month_control_microtopics_detailed(callback, state, group_id, month_test_id, student_id)

    except (ValueError, IndexError):
        await callback.message.edit_text(
            "❌ Ошибка: неверные параметры",
            reply_markup=get_back_kb()
        )


async def show_month_control_summary_microtopics(callback: CallbackQuery, state: FSMContext):
    """Показать сводку по сильным/слабым темам контрольного теста месяца"""
    current_state = await state.get_state()
    logger.info(f"ВЫЗОВ: show_month_control_summary_microtopics, user_id={callback.from_user.id}, текущее состояние={current_state}, callback_data={callback.data}")

    try:
        # Формат: month_control_summary_GROUP_ID_MONTH_TEST_ID_STUDENT_ID
        parts = callback.data.split("_")
        group_id = int(parts[3])
        month_test_id = int(parts[4])
        student_id = int(parts[5])

        await show_month_control_microtopics_summary(callback, state, group_id, month_test_id, student_id)

    except (ValueError, IndexError):
        await callback.message.edit_text(
            "❌ Ошибка: неверные параметры",
            reply_markup=get_back_kb()
        )


async def show_month_control_microtopics_detailed(callback: CallbackQuery, state: FSMContext, group_id: int, month_test_id: int, student_id: int):
    """Показать детальную статистику по микротемам контрольного теста месяца с сравнением"""
    from database import (
        MonthEntryTestResultRepository,
        StudentRepository, GroupRepository, MonthTestRepository, MicrotopicRepository
    )

    try:
        # Получаем студента, группу и тест месяца
        student = await StudentRepository.get_by_id(student_id)
        group = await GroupRepository.get_by_id(group_id)
        month_test = await MonthTestRepository.get_by_id(month_test_id)

        if not student or not group or not month_test:
            await callback.message.edit_text(
                "❌ Студент, группа или контрольный тест месяца не найдены",
                reply_markup=get_back_kb()
            )
            return

        # Получаем названия микротем
        microtopics = await MicrotopicRepository.get_by_subject(group.subject_id)
        microtopic_names = {mt.number: mt.name for mt in microtopics}

        # Пытаемся получить сравнительную статистику
        entry_test = None
        if month_test.parent_test_id:
            entry_test = await MonthTestRepository.get_by_id(month_test.parent_test_id)

        if entry_test:
            # Получаем сравнительную статистику
            comparison_data = await MonthEntryTestResultRepository.get_comparison_statistics(
                student_id, entry_test.id, month_test_id
            )

            if comparison_data:
                # Показываем сравнение
                result_text = f"📊 Детальная статистика контрольного теста месяца\n\n"
                result_text += f"👤 {student.user.name}\n"
                result_text += f"📗 {group.subject.name}:\n"
                result_text += f"Тест: {month_test.name}\n"

                entry_data = comparison_data['entry_test']
                control_data = comparison_data['control_test']
                comparison = comparison_data['comparison']

                result_text += f"Верных: {entry_data['correct_answers']} / {entry_data['total_questions']} → {control_data['correct_answers']} / {control_data['total_questions']}\n\n"

                result_text += "📊 % правильных ответов по микротемам:\n"

                # Показываем сравнение по микротемам
                microtopic_changes = comparison['microtopic_changes']
                if microtopic_changes:
                    for microtopic_num in sorted(microtopic_changes.keys()):
                        change_data = microtopic_changes[microtopic_num]
                        microtopic_name = microtopic_names.get(microtopic_num, f"Микротема {microtopic_num}")

                        entry_percentage = change_data['entry_percentage']
                        control_percentage = change_data['control_percentage']
                        growth_percentage = change_data.get('growth_percentage', 0)

                        # Определяем эмодзи по проценту контрольного теста
                        if control_percentage >= 80:
                            emoji = "✅"
                        elif control_percentage <= 40:
                            emoji = "❌"
                        else:
                            emoji = "⚠️"

                        # Показываем сравнение с ростом
                        if entry_percentage == 0 and control_percentage > 0:
                            # Абсолютный рост в процентных пунктах
                            result_text += f"• {microtopic_name} — {entry_percentage}% → {control_percentage}% (+{control_percentage:.0f} п.п.) {emoji}\n"
                        elif entry_percentage > 0:
                            # Относительный рост в процентах
                            if growth_percentage > 0:
                                result_text += f"• {microtopic_name} — {entry_percentage}% → {control_percentage}% (+{growth_percentage:.1f}%) {emoji}\n"
                            elif growth_percentage < 0:
                                result_text += f"• {microtopic_name} — {entry_percentage}% → {control_percentage}% ({growth_percentage:.1f}%) {emoji}\n"
                            else:
                                result_text += f"• {microtopic_name} — {entry_percentage}% → {control_percentage}% {emoji}\n"
                        else:
                            # Оба теста 0%
                            result_text += f"• {microtopic_name} — {entry_percentage}% → {control_percentage}% {emoji}\n"
                else:
                    result_text += "Нет данных по микротемам\n"
            else:
                # Если сравнение не удалось получить, показываем только контрольный тест
                await show_month_control_fallback_detailed(callback, student, group, month_test, month_test_id, student_id, microtopic_names)
                return
        else:
            # Если входной тест не найден, показываем только контрольный тест
            await show_month_control_fallback_detailed(callback, student, group, month_test, month_test_id, student_id, microtopic_names)
            return

        await callback.message.edit_text(
            result_text,
            reply_markup=get_back_kb()
        )

    except Exception as e:
        logger.error(f"Ошибка при получении детальной статистики контрольного теста месяца: {e}")
        await callback.message.edit_text(
            "❌ Ошибка при получении статистики",
            reply_markup=get_back_kb()
        )


async def show_month_control_fallback_detailed(callback, student, group, month_test, month_test_id, student_id, microtopic_names):
    """Показать детальную статистику только контрольного теста (без сравнения)"""
    from database import MonthEntryTestResultRepository

    # Получаем результат теста
    test_result = await MonthEntryTestResultRepository.get_by_student_and_month_test(
        student_id, month_test_id
    )

    if not test_result:
        await callback.message.edit_text(
            f"❌ {student.user.name} еще не проходил контрольный тест месяца '{month_test.name}'",
            reply_markup=get_back_kb()
        )
        return

    # Получаем статистику по микротемам
    microtopic_stats = await MonthEntryTestResultRepository.get_microtopic_statistics(test_result.id)

    # Формируем детальную статистику
    result_text = f"📊 Детальная статистика контрольного теста месяца\n\n"
    result_text += f"👤 {student.user.name}\n"
    result_text += f"📗 {group.subject.name}:\n"
    result_text += f"Тест: {month_test.name}\n"
    result_text += f"Верных: {test_result.correct_answers} / {test_result.total_questions}\n\n"
    result_text += "📊 % правильных ответов по микротемам:\n"

    if microtopic_stats:
        for microtopic_num in sorted(microtopic_stats.keys()):
            stats = microtopic_stats[microtopic_num]
            microtopic_name = microtopic_names.get(microtopic_num, f"Микротема {microtopic_num}")
            percentage = stats['percentage']

            # Определяем эмодзи статуса
            if percentage >= 80:
                status = "✅"
            elif percentage <= 40:
                status = "❌"
            else:
                status = "⚠️"

            result_text += f"• {microtopic_name} — {percentage}% {status}\n"
    else:
        result_text += "Нет данных по микротемам\n"

    await callback.message.edit_text(
        result_text,
        reply_markup=get_back_kb()
    )


async def show_month_control_microtopics_summary(callback: CallbackQuery, state: FSMContext, group_id: int, month_test_id: int, student_id: int):
    """Показать сводку по сильным/слабым темам контрольного теста месяца"""
    from database import MonthEntryTestResultRepository, StudentRepository, GroupRepository, MonthTestRepository, MicrotopicRepository

    try:
        # Получаем студента, группу и тест месяца
        student = await StudentRepository.get_by_id(student_id)
        group = await GroupRepository.get_by_id(group_id)
        month_test = await MonthTestRepository.get_by_id(month_test_id)

        if not student or not group or not month_test:
            await callback.message.edit_text(
                "❌ Студент, группа или контрольный тест месяца не найдены",
                reply_markup=get_back_kb()
            )
            return

        # Получаем результат теста
        test_result = await MonthEntryTestResultRepository.get_by_student_and_month_test(
            student_id, month_test_id
        )

        if not test_result:
            await callback.message.edit_text(
                f"❌ {student.user.name} еще не проходил контрольный тест месяца '{month_test.name}'",
                reply_markup=get_back_kb()
            )
            return

        # Получаем статистику по микротемам
        microtopic_stats = await MonthEntryTestResultRepository.get_microtopic_statistics(test_result.id)

        # Получаем названия микротем
        microtopics = await MicrotopicRepository.get_by_subject(group.subject_id)
        microtopic_names = {mt.number: mt.name for mt in microtopics}

        # Определяем сильные и слабые темы
        strong_topics = []
        weak_topics = []

        for microtopic_num, stats in microtopic_stats.items():
            microtopic_name = microtopic_names.get(microtopic_num, f"Микротема {microtopic_num}")
            percentage = stats['percentage']

            if percentage >= 80:
                strong_topics.append(microtopic_name)
            elif percentage <= 40:
                weak_topics.append(microtopic_name)

        # Формируем сводку
        result_text = f"💪 Сводка по контрольному тесту месяца\n\n"
        result_text += f"👤 {student.user.name}\n"
        result_text += f"📗 {group.subject.name}:\n"
        result_text += f"Тест: {month_test.name}\n"
        result_text += f"Верных: {test_result.correct_answers} / {test_result.total_questions}\n\n"

        if strong_topics:
            result_text += "🟢 Сильные темы (≥80%):\n"
            for topic in strong_topics:
                result_text += f"• {topic}\n"

        if weak_topics:
            if strong_topics:
                result_text += "\n"
            result_text += "🔴 Слабые темы (≤40%):\n"
            for topic in weak_topics:
                result_text += f"• {topic}\n"

        if not strong_topics and not weak_topics:
            result_text += "⚠️ Все темы находятся в среднем диапазоне (41-79%)"

        await callback.message.edit_text(
            result_text,
            reply_markup=get_back_kb()
        )

    except Exception as e:
        logger.error(f"Ошибка при получении сводки контрольного теста месяца: {e}")
        await callback.message.edit_text(
            "❌ Ошибка при получении сводки",
            reply_markup=get_back_kb()
        )


# Функция для сравнения входного и контрольного тестов месяца
async def show_month_tests_comparison(callback: CallbackQuery, state: FSMContext):
    """Показать сравнение входного и контрольного тестов месяца"""
    current_state = await state.get_state()
    logger.info(f"ВЫЗОВ: show_month_tests_comparison, user_id={callback.from_user.id}, текущее состояние={current_state}, callback_data={callback.data}")

    try:
        # Формат: month_comparison_GROUP_ID_MONTH_TEST_ID_STUDENT_ID
        parts = callback.data.split("_")
        group_id = int(parts[2])
        control_test_id = int(parts[3])  # ID контрольного теста
        student_id = int(parts[4])

        await show_month_tests_comparison_detail(callback, state, group_id, control_test_id, student_id)

    except (ValueError, IndexError):
        await callback.message.edit_text(
            "❌ Ошибка: неверные параметры",
            reply_markup=get_back_kb()
        )


async def show_month_tests_comparison_detail(callback: CallbackQuery, state: FSMContext, group_id: int, control_test_id: int, student_id: int):
    """Показать детальное сравнение входного и контрольного тестов месяца"""
    from database import (
        MonthEntryTestResultRepository,
        StudentRepository, GroupRepository, MonthTestRepository, MicrotopicRepository
    )

    try:
        # Получаем студента, группу и контрольный тест месяца
        student = await StudentRepository.get_by_id(student_id)
        group = await GroupRepository.get_by_id(group_id)
        control_test = await MonthTestRepository.get_by_id(control_test_id)

        if not student or not group or not control_test:
            await callback.message.edit_text(
                "❌ Студент, группа или контрольный тест месяца не найдены",
                reply_markup=get_back_kb()
            )
            return

        # Находим соответствующий входной тест
        entry_test = None
        if control_test.parent_test_id:
            entry_test = await MonthTestRepository.get_by_id(control_test.parent_test_id)

        if not entry_test:
            await callback.message.edit_text(
                f"❌ Не найден соответствующий входной тест для контрольного теста '{control_test.name}'",
                reply_markup=get_back_kb()
            )
            return

        # Получаем результаты обоих тестов
        entry_result = await MonthEntryTestResultRepository.get_by_student_and_month_test(
            student_id, entry_test.id
        )
        control_result = await MonthEntryTestResultRepository.get_by_student_and_month_test(
            student_id, control_test_id
        )

        if not entry_result:
            await callback.message.edit_text(
                f"❌ {student.user.name} не проходил входной тест месяца '{entry_test.name}'",
                reply_markup=get_back_kb()
            )
            return

        if not control_result:
            await callback.message.edit_text(
                f"❌ {student.user.name} не проходил контрольный тест месяца '{control_test.name}'",
                reply_markup=get_back_kb()
            )
            return

        # Получаем сравнительную статистику
        comparison_data = await MonthEntryTestResultRepository.get_comparison_statistics(
            student_id, entry_test.id, control_test_id
        )

        if not comparison_data:
            await callback.message.edit_text(
                "❌ Ошибка при получении сравнительной статистики",
                reply_markup=get_back_kb()
            )
            return

        # Получаем названия микротем
        microtopics = await MicrotopicRepository.get_by_subject(group.subject_id)
        microtopic_names = {mt.number: mt.name for mt in microtopics}

        # Формируем текст сравнения
        result_text = f"🧾 Сравнение входного и контрольного теста месяца\n\n"
        result_text += f"👤 {student.user.name}\n"
        result_text += f"📗 {group.subject.name}:\n"

        # Общие результаты
        entry_data = comparison_data['entry_test']
        control_data = comparison_data['control_test']
        comparison = comparison_data['comparison']

        result_text += f"Верных: {entry_data['correct_answers']} / {entry_data['total_questions']} → {control_data['correct_answers']} / {control_data['total_questions']}\n"

        # Результаты по микротемам
        microtopic_changes = comparison['microtopic_changes']
        if microtopic_changes:
            for microtopic_num in sorted(microtopic_changes.keys()):
                change_data = microtopic_changes[microtopic_num]
                microtopic_name = microtopic_names.get(microtopic_num, f"Микротема {microtopic_num}")

                entry_percentage = change_data['entry_percentage']
                control_percentage = change_data['control_percentage']
                growth_percentage = change_data.get('growth_percentage', 0)

                # Определяем стрелку изменения и показываем рост
                if entry_percentage == 0 and growth_percentage < 0:
                    # Абсолютный рост (отрицательное значение как флаг)
                    absolute_growth = -growth_percentage
                    arrow = f"📈 (+{absolute_growth:.1f} п.п.)"
                elif growth_percentage > 0:
                    arrow = f"↗️ (+{growth_percentage:.1f}%)"
                elif growth_percentage < 0:
                    arrow = f"↘️ ({growth_percentage:.1f}%)"
                else:
                    arrow = "→"

                result_text += f"• {microtopic_name} — {entry_percentage}% → {control_percentage}% {arrow}\n"

        # Общий прирост по новой формуле: ((B - A) / A) × 100%
        entry_percentage = entry_data['score_percentage']
        control_percentage = control_data['score_percentage']

        if entry_percentage > 0:  # Избегаем деления на ноль
            growth_percentage = ((control_percentage - entry_percentage) / entry_percentage) * 100
            if growth_percentage > 0:
                result_text += f"📈 Общий рост: +{growth_percentage:.1f}%\n"
            elif growth_percentage < 0:
                result_text += f"📉 Общее снижение: {growth_percentage:.1f}%\n"
            else:
                result_text += f"📊 Результат остался на том же уровне\n"
        else:
            # Если входной тест 0%, показываем абсолютный рост в процентных пунктах
            if control_percentage > 0:
                result_text += f"📈 Рост: +{control_percentage:.1f} п.п.\n"  # п.п. = процентные пункты
            else:
                result_text += f"📊 Оба теста показали 0%\n"

        await callback.message.edit_text(
            result_text,
            reply_markup=get_back_kb()
        )

    except Exception as e:
        logger.error(f"Ошибка при получении сравнения тестов месяца: {e}")
        await callback.message.edit_text(
            "❌ Ошибка при получении сравнения тестов",
            reply_markup=get_back_kb()
        )



