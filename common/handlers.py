from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from student.handlers.homework import show_main_menu as student_main_menu
from curator.handlers.main import show_curator_main_menu

# Импортируем все необходимые состояния
from student.handlers.homework import HomeworkStates
from student.handlers.progress import ProgressStates
from student.handlers.shop import ShopStates
from student.handlers.test_report import TestReportStates
from student.handlers.trial_ent import TrialEntStates
from student.handlers.curator_contact import CuratorStates
from student.handlers.account import AccountStates
from curator.handlers.groups import CuratorGroupStates
from curator.handlers.homeworks import HomeworkStates as CuratorHomeworkStates
from curator.handlers.messages import MessageStates
from curator.handlers.analytics import AnalyticsStates
from curator.handlers.main import CuratorMainStates

router = Router()

# Словарь переходов для состояний студента
STUDENT_STATE_TRANSITIONS = {
    # Домашние задания
    HomeworkStates.course.state: None,
    HomeworkStates.subject.state: HomeworkStates.course.state,
    HomeworkStates.lesson.state: HomeworkStates.subject.state,
    HomeworkStates.homework.state: HomeworkStates.lesson.state,
    HomeworkStates.confirmation.state: HomeworkStates.homework.state,
    HomeworkStates.test_in_progress.state: HomeworkStates.confirmation.state,
    
    # Прогресс
    ProgressStates.main.state: None,
    
    # Магазин
    ShopStates.main.state: None,
    ShopStates.exchange.state: ShopStates.main.state,
    ShopStates.catalog.state: ShopStates.main.state,
    ShopStates.my_bonuses.state: ShopStates.main.state,
    
    # Тест-отчет
    TestReportStates.main.state: None,
    
    # Пробный ЕНТ
    TrialEntStates.main.state: None,
    TrialEntStates.required_subjects.state: TrialEntStates.main.state,
    TrialEntStates.profile_subjects.state: TrialEntStates.required_subjects.state,
    TrialEntStates.second_profile_subject.state: TrialEntStates.profile_subjects.state,
    TrialEntStates.test_in_progress.state: None,
    TrialEntStates.results.state: None,
    TrialEntStates.analytics_subjects.state: TrialEntStates.results.state,
    TrialEntStates.subject_analytics.state: TrialEntStates.analytics_subjects.state,
    
    # Связь с куратором
    CuratorStates.main.state: None,
    CuratorStates.curator_info.state: CuratorStates.main.state,
    
    # Аккаунт
    AccountStates.main.state: None,
}

# Словарь переходов для состояний куратора
CURATOR_STATE_TRANSITIONS = {
    # Главное меню
    CuratorMainStates.main.state: None,
    
    # Группы
    CuratorGroupStates.select_group.state: None,
    CuratorGroupStates.select_student.state: CuratorGroupStates.select_group.state,
    CuratorGroupStates.student_profile.state: CuratorGroupStates.select_student.state,
    
    # Домашние задания
    CuratorHomeworkStates.main.state: None,
    CuratorHomeworkStates.student_stats_course.state: CuratorHomeworkStates.main.state,
    CuratorHomeworkStates.student_stats_group.state: CuratorHomeworkStates.student_stats_course.state,
    CuratorHomeworkStates.student_stats_subject.state: CuratorHomeworkStates.student_stats_group.state,
    CuratorHomeworkStates.student_stats_lesson.state: CuratorHomeworkStates.student_stats_subject.state,
    CuratorHomeworkStates.student_stats_list.state: CuratorHomeworkStates.student_stats_lesson.state,
    CuratorHomeworkStates.group_stats_group.state: CuratorHomeworkStates.main.state,
    
    # Сообщения
    MessageStates.main.state: None,
    MessageStates.select_group.state: MessageStates.main.state,
    MessageStates.select_student.state: MessageStates.select_group.state,
    MessageStates.enter_individual_message.state: MessageStates.select_student.state,
    MessageStates.confirm_individual_message.state: MessageStates.enter_individual_message.state,
    MessageStates.enter_mass_message.state: MessageStates.main.state,
    MessageStates.confirm_mass_message.state: MessageStates.enter_mass_message.state,
    
    # Аналитика
    AnalyticsStates.main.state: None,
    AnalyticsStates.select_group_for_student.state: AnalyticsStates.main.state,
    AnalyticsStates.select_student.state: AnalyticsStates.select_group_for_student.state,
    AnalyticsStates.student_stats.state: AnalyticsStates.select_student.state,
    AnalyticsStates.select_group_for_group.state: AnalyticsStates.main.state,
    AnalyticsStates.group_stats.state: AnalyticsStates.select_group_for_group.state,
}

# Объединяем все переходы в один словарь
STATE_TRANSITIONS = {**STUDENT_STATE_TRANSITIONS, **CURATOR_STATE_TRANSITIONS}

# Словарь обработчиков для состояний студента
from student.handlers.homework import (
    choose_course, choose_subject, choose_lesson, 
    choose_homework, confirm_homework
)
from student.handlers.progress import show_progress_menu
from student.handlers.shop import show_shop_menu
from student.handlers.test_report import show_test_report_menu
from student.handlers.trial_ent import (
    show_trial_ent_menu, choose_required_subjects, 
    choose_profile_subjects, show_analytics_subjects
)
from student.handlers.curator_contact import show_curator_menu
from student.handlers.account import show_account_info

# Словарь обработчиков для состояний куратора
from curator.handlers.groups import show_curator_groups, show_group_students
from curator.handlers.homeworks import (
    show_homework_menu, select_student_stats_course, 
    select_student_stats_group, select_student_stats_subject,
    select_student_stats_lesson
)
from curator.handlers.messages import (
    show_messages_menu, select_group_for_individual
)
from curator.handlers.analytics import (
    show_analytics_menu, select_group_for_student_analytics,
    select_group_for_group_analytics
)

# Объединяем обработчики в один словарь
STUDENT_STATE_HANDLERS = {
    None: student_main_menu,
    HomeworkStates.course.state: choose_course,
    HomeworkStates.subject.state: choose_subject,
    HomeworkStates.lesson.state: choose_lesson,
    HomeworkStates.homework.state: choose_homework,
    HomeworkStates.confirmation.state: confirm_homework,
    
    ProgressStates.main.state: show_progress_menu,
    ShopStates.main.state: show_shop_menu,
    TestReportStates.main.state: show_test_report_menu,
    
    TrialEntStates.main.state: show_trial_ent_menu,
    TrialEntStates.required_subjects.state: choose_required_subjects,
    TrialEntStates.profile_subjects.state: choose_profile_subjects,
    TrialEntStates.analytics_subjects.state: show_analytics_subjects,
    
    CuratorStates.main.state: show_curator_menu,
    AccountStates.main.state: show_account_info,
}

CURATOR_STATE_HANDLERS = {
    None: show_curator_main_menu,
    CuratorMainStates.main.state: show_curator_main_menu,
    
    CuratorGroupStates.select_group.state: show_curator_groups,
    CuratorGroupStates.select_student.state: show_group_students,
    
    CuratorHomeworkStates.main.state: show_homework_menu,
    CuratorHomeworkStates.student_stats_course.state: select_student_stats_course,
    CuratorHomeworkStates.student_stats_group.state: select_student_stats_group,
    CuratorHomeworkStates.student_stats_subject.state: select_student_stats_subject,
    CuratorHomeworkStates.student_stats_lesson.state: select_student_stats_lesson,
    
    MessageStates.main.state: show_messages_menu,
    MessageStates.select_group.state: select_group_for_individual,
    
    AnalyticsStates.main.state: show_analytics_menu,
    AnalyticsStates.select_group_for_student.state: select_group_for_student_analytics,
    AnalyticsStates.select_group_for_group.state: select_group_for_group_analytics,
}

# Объединяем все обработчики
STATE_HANDLERS = {**STUDENT_STATE_HANDLERS, **CURATOR_STATE_HANDLERS}

@router.callback_query(F.data == "back")
async def go_back(callback: CallbackQuery, state: FSMContext, user_role: str = None):
    current_state = await state.get_state()
    
    # Если состояния нет или оно не в словаре переходов
    if not current_state or current_state not in STATE_TRANSITIONS:
        # Возвращаемся в главное меню в зависимости от роли
        await callback.message.delete()
        if user_role == "curator":
            await show_curator_main_menu(callback.message)
        else:  # По умолчанию считаем пользователя студентом
            await student_main_menu(callback.message)
        await state.clear()
        return

    # Получаем предыдущее состояние из словаря переходов
    prev_state = STATE_TRANSITIONS[current_state]

    if prev_state is None:
        # Если предыдущее состояние None, возвращаемся в главное меню в зависимости от роли
        await callback.message.delete()
        if user_role == "curator":
            await show_curator_main_menu(callback.message)
        else:  # По умолчанию считаем пользователя студентом
            await student_main_menu(callback.message)
        await state.clear()
        return

    # Вызываем соответствующий обработчик для предыдущего состояния
    if prev_state in STATE_HANDLERS:
        await STATE_HANDLERS[prev_state](callback, state)
    else:
        # Если обработчик не найден, возвращаемся в главное меню
        await callback.message.delete()
        if user_role == "curator":
            await show_curator_main_menu(callback.message)
        else:  # По умолчанию считаем пользователя студентом
            await student_main_menu(callback.message)
        await state.clear()