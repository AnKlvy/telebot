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

    # Получаем группы куратора из базы данных
    from database import CuratorRepository, UserRepository

    # Получаем куратора по telegram_id
    user = await UserRepository.get_by_telegram_id(callback.from_user.id)
    if not user:
        await callback.message.edit_text(
            "❌ Пользователь не найден в системе",
            reply_markup=get_back_kb()
        )
        return

    curator = await CuratorRepository.get_by_user_id(user.id)
    if not curator:
        await callback.message.edit_text(
            "❌ Профиль куратора не найден",
            reply_markup=get_back_kb()
        )
        return

    # Получаем группы куратора
    curator_groups = await CuratorRepository.get_curator_groups(curator.id)
    if not curator_groups:
        await callback.message.edit_text(
            "❌ У вас нет назначенных групп",
            reply_markup=get_back_kb()
        )
        return

    await callback.message.edit_text(
        "Выберите группу для просмотра статистики входного теста курса:",
        reply_markup=await get_curator_groups_kb("course_entry", curator_groups)
    )

@router.callback_query(F.data.startswith("course_entry_group_"))
async def show_course_entry_statistics(callback: CallbackQuery, state: FSMContext):
    """Показать статистику входного теста курса для группы"""
    current_state = await state.get_state()
    logger.info(f"ВЫЗОВ: show_course_entry_statistics, user_id={callback.from_user.id}, текущее состояние={current_state}, callback_data={callback.data}")

    try:
        group_id = int(callback.data.replace("course_entry_group_", ""))
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
    await callback.message.edit_text(
        "Выберите группу для просмотра статистики входного теста месяца:",
        reply_markup=get_groups_kb("month_entry")
    )

@router.callback_query(F.data.startswith("month_entry_group_"))
async def show_month_entry_months(callback: CallbackQuery, state: FSMContext):
    """Показать месяцы для входного теста месяца"""
    current_state = await state.get_state()
    logger.info(f"ВЫЗОВ: show_month_entry_months, user_id={callback.from_user.id}, текущее состояние={current_state}, callback_data={callback.data}")
    group_id = await get_group_id_from_callback_or_state(callback, state, "month_entry_group_")
    
    await callback.message.edit_text(
        "Выберите месяц для просмотра статистики входного теста:",
        reply_markup=get_month_kb("month_entry", group_id)
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
    # Формат: month_entry_month_GROUP_ID_MONTH_ID
    parts = callback.data.split("_")
    group_id = parts[3]
    month_id = parts[4]
    await show_test_students_statistics(callback, state, "month_entry", group_id, month_id)

@router.callback_query(F.data.startswith("month_entry_student_"))
async def show_month_entry_student_statistics(callback: CallbackQuery, state: FSMContext):
    """Показать статистику входного теста месяца для конкретного ученика"""
    current_state = await state.get_state()
    logger.info(f"ВЫЗОВ: show_month_entry_student_statistics, user_id={callback.from_user.id}, текущее состояние={current_state}, callback_data={callback.data}")
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
    current_state = await state.get_state()
    logger.info(f"ВЫЗОВ: show_month_control_groups, user_id={callback.from_user.id}, текущее состояние={current_state}, callback_data={callback.data}")
    await callback.message.edit_text(
        "Выберите группу для просмотра статистики контрольного теста месяца:",
        reply_markup=get_groups_kb("month_control")
    )

@router.callback_query(F.data.startswith("month_control_group_"))
async def show_month_control_months(callback: CallbackQuery, state: FSMContext):
    """Показать месяцы для контрольного теста месяца"""
    current_state = await state.get_state()
    logger.info(f"ВЫЗОВ: show_month_control_months, user_id={callback.from_user.id}, текущее состояние={current_state}, callback_data={callback.data}")
    group_id = await get_group_id_from_callback_or_state(callback, state, "month_control_group_")
    
    await callback.message.edit_text(
        "Выберите месяц для просмотра статистики контрольного теста:",
        reply_markup=get_month_kb("month_control", group_id)
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
    # Формат: month_control_month_GROUP_ID_MONTH_ID
    parts = callback.data.split("_")
    group_id = parts[3]
    month_id = parts[4]
    await show_test_students_statistics(callback, state, "month_control", group_id, month_id)

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
    await callback.message.edit_text(
        "Выберите группу для просмотра статистики пробного ЕНТ:",
        reply_markup=get_groups_kb("ent")
    )

@router.callback_query(F.data.startswith("ent_group_"))
async def show_ent_students(callback: CallbackQuery, state: FSMContext):
    """Показать студентов для пробного ЕНТ"""
    current_state = await state.get_state()
    logger.info(f"ВЫЗОВ: show_ent_students, user_id={callback.from_user.id}, текущее состояние={current_state}, callback_data={callback.data}")
    group_id = await get_group_id_from_callback_or_state(callback, state, "ent_group_")
    
    await callback.message.edit_text(
        "Выберите ученика для просмотра статистики пробного ЕНТ:",
        reply_markup=get_students_kb("ent", group_id)
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
