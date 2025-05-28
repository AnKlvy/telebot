import logging
from aiogram import F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from common.tests_statistics.menu import show_tests_statistics_menu
from common.tests_statistics.handlers import (
    show_course_entry_groups, show_month_entry_groups, show_month_entry_months,
    show_course_entry_statistics, show_month_entry_statistics,
    show_month_control_groups, show_month_control_months, show_month_control_statistics,
    show_ent_groups, show_ent_students, show_ent_statistics,
show_tests_comparison,
)

def get_transitions_handlers(states_group, role):
    """
    Создает словари переходов и обработчиков для статистики тестов
    
    Args:
        states_group: Группа состояний (CuratorTestsStatisticsStates или TeacherTestsStatisticsStates)
        role: Роль пользователя ('curator' или 'teacher')
        
    Returns:
        tuple: (STATE_TRANSITIONS, STATE_HANDLERS) - словари переходов и обработчиков
    """
    # Создаем словарь переходов между состояниями
    STATE_TRANSITIONS = {
        states_group.main: None,  # None означает возврат в главное меню
        
        # Переходы для входного теста курса
        states_group.course_entry_select_group: states_group.main,
        states_group.course_entry_result: states_group.course_entry_select_group,
        
        # Переходы для входного теста месяца
        states_group.month_entry_select_group: states_group.main,
        states_group.month_entry_select_month: states_group.month_entry_select_group,
        states_group.month_entry_result: states_group.month_entry_select_month,
        
        # Переходы для контрольного теста месяца
        states_group.month_control_select_group: states_group.main,
        states_group.month_control_select_month: states_group.month_control_select_group,
        states_group.month_control_result: states_group.month_control_select_month,
        
        # Переходы для пробного ЕНТ
        states_group.ent_select_group: states_group.main,
        states_group.ent_select_student: states_group.ent_select_group,
        states_group.ent_result: states_group.ent_select_student
    }
    
    # Создаем словарь обработчиков для каждого состояния
    STATE_HANDLERS = {
        states_group.main: lambda callback, state: show_tests_statistics_menu(callback, state, role),
        
        # Обработчики для входного теста курса
        states_group.course_entry_select_group: show_course_entry_groups,
        states_group.course_entry_result: show_course_entry_statistics,
        
        # Обработчики для входного теста месяца
        states_group.month_entry_select_group: show_month_entry_groups,
        states_group.month_entry_select_month: show_month_entry_months,
        states_group.month_entry_result: show_month_entry_statistics,
        
        # Обработчики для контрольного теста месяца
        states_group.month_control_select_group: show_month_control_groups,
        states_group.month_control_select_month: show_month_control_months,
        states_group.month_control_result: show_month_control_statistics,
        
        # Обработчики для пробного ЕНТ
        states_group.ent_select_group: show_ent_groups,
        states_group.ent_select_student: show_ent_students,
        states_group.ent_result: show_ent_statistics
    }
    
    return STATE_TRANSITIONS, STATE_HANDLERS

def register_test_statistics_handlers(router, states_group, role):
    """
    Регистрирует обработчики для статистики тестов
    
    Args:
        router: Роутер для регистрации обработчиков
        states_group: Группа состояний (CuratorTestsStatisticsStates или TeacherTestsStatisticsStates)
        role: Роль пользователя ('curator' или 'teacher')
    """
    logger = logging.getLogger(__name__)
    
    # Обработчик для главного меню статистики тестов
    @router.callback_query(F.data == f"{role}_tests")
    async def show_role_tests_statistics(callback: CallbackQuery, state: FSMContext):
        """Показать меню статистики тестов"""
        logger.info(f"Вызвана функция show_tests_statistics для пользователя {callback.from_user.id}")
        await show_tests_statistics_menu(callback, state, role)
        await state.set_state(states_group.main)
    
    # Регистрируем обработчики для различных типов тестов
    
    # Входной тест курса
    @router.callback_query(states_group.main, F.data == "stats_course_entry_test")
    async def role_show_course_entry_groups_handler(callback: CallbackQuery, state: FSMContext):
        logger.info(f"Вызвана функция show_course_entry_groups для пользователя {callback.from_user.id}")
        await show_course_entry_groups(callback, state)
        await state.set_state(states_group.course_entry_select_group)
    
    @router.callback_query(states_group.course_entry_select_group, F.data.startswith("course_entry_group_"))
    async def role_show_course_entry_statistics_handler(callback: CallbackQuery, state: FSMContext):
        logger.info(f"Вызвана функция show_course_entry_statistics для пользователя {callback.from_user.id}")
        await show_course_entry_statistics(callback, state)
        await state.set_state(states_group.course_entry_result)
    
    # Добавляем обработчик для перехода к статистике конкретного студента
    @router.callback_query(states_group.course_entry_result, F.data.startswith("course_entry_student_"))
    async def role_show_course_entry_student_statistics_handler(callback: CallbackQuery, state: FSMContext):
        logger.info(f"Вызвана функция show_course_entry_student_statistics для пользователя {callback.from_user.id}")
        from common.tests_statistics.handlers import show_course_entry_student_statistics
        await show_course_entry_student_statistics(callback, state)
        # Остаемся в том же состоянии
        await state.set_state(states_group.course_entry_result)
    
    # Входной тест месяца
    @router.callback_query(states_group.main, F.data == "stats_month_entry_test")
    async def role_show_month_entry_groups_handler(callback: CallbackQuery, state: FSMContext):
        logger.info(f"Вызвана функция show_month_entry_groups для пользователя {callback.from_user.id}")
        await show_month_entry_groups(callback, state)
        await state.set_state(states_group.month_entry_select_group)
    
    @router.callback_query(states_group.month_entry_select_group, F.data.startswith("month_entry_group_"))
    async def role_show_month_entry_months_handler(callback: CallbackQuery, state: FSMContext):
        logger.info(f"Вызвана функция show_month_entry_months для пользователя {callback.from_user.id}")
        await show_month_entry_months(callback, state)
        await state.set_state(states_group.month_entry_select_month)
    
    @router.callback_query(states_group.month_entry_select_month, F.data.startswith("month_entry_month_"))
    async def role_show_month_entry_statistics_handler(callback: CallbackQuery, state: FSMContext):
        logger.info(f"Вызвана функция show_month_entry_statistics для пользователя {callback.from_user.id}")
        await show_month_entry_statistics(callback, state)
        await state.set_state(states_group.month_entry_result)
    
    # Добавляем обработчик для перехода к статистике конкретного студента
    @router.callback_query(states_group.month_entry_result, F.data.startswith("month_entry_student_"))
    async def role_show_month_entry_student_statistics_handler(callback: CallbackQuery, state: FSMContext):
        logger.info(f"Вызвана функция show_month_entry_student_statistics для пользователя {callback.from_user.id}")
        from common.tests_statistics.handlers import show_month_entry_student_statistics
        await show_month_entry_student_statistics(callback, state)
        # Остаемся в том же состоянии
        await state.set_state(states_group.month_entry_result)
    
    # Контрольный тест месяца
    @router.callback_query(states_group.main, F.data == "stats_month_control_test")
    async def role_show_month_control_groups_handler(callback: CallbackQuery, state: FSMContext):
        logger.info(f"Вызвана функция show_month_control_groups для пользователя {callback.from_user.id}")
        await show_month_control_groups(callback, state)
        await state.set_state(states_group.month_control_select_group)
    
    @router.callback_query(states_group.month_control_select_group, F.data.startswith("month_control_group_"))
    async def role_show_month_control_months_handler(callback: CallbackQuery, state: FSMContext):
        logger.info(f"Вызвана функция show_month_control_months для пользователя {callback.from_user.id}")
        await show_month_control_months(callback, state)
        await state.set_state(states_group.month_control_select_month)
    
    @router.callback_query(states_group.month_control_select_month, F.data.startswith("month_control_month_"))
    async def role_show_month_control_statistics_handler(callback: CallbackQuery, state: FSMContext):
        logger.info(f"Вызвана функция show_month_control_statistics для пользователя {callback.from_user.id}")
        await show_month_control_statistics(callback, state)
        await state.set_state(states_group.month_control_result)
    
    # Добавляем обработчик для перехода к статистике конкретного студента
    @router.callback_query(states_group.month_control_result, F.data.startswith("month_control_student_"))
    async def role_show_month_control_student_statistics_handler(callback: CallbackQuery, state: FSMContext):
        logger.info(f"Вызвана функция show_month_control_student_statistics для пользователя {callback.from_user.id}")
        await show_tests_comparison(callback, state)
        # Остаемся в том же состоянии
        await state.set_state(states_group.month_control_result)
    
    # Пробное ЕНТ
    @router.callback_query(states_group.main, F.data == "stats_ent_test")
    async def role_show_ent_groups_handler(callback: CallbackQuery, state: FSMContext):
        logger.info(f"Вызвана функция show_ent_groups для пользователя {callback.from_user.id}")
        await show_ent_groups(callback, state)
        await state.set_state(states_group.ent_select_group)
    
    @router.callback_query(states_group.ent_select_group, F.data.startswith("ent_group_"))
    async def role_show_ent_students_handler(callback: CallbackQuery, state: FSMContext):
        logger.info(f"Вызвана функция show_ent_students для пользователя {callback.from_user.id}")
        await show_ent_students(callback, state)
        await state.set_state(states_group.ent_select_student)
    
    @router.callback_query(states_group.ent_select_student, F.data.startswith("ent_student_"))
    async def role_show_ent_statistics_handler(callback: CallbackQuery, state: FSMContext):
        logger.info(f"Вызвана функция show_ent_statistics для пользователя {callback.from_user.id}")
        await show_ent_statistics(callback, state)
        await state.set_state(states_group.ent_result)