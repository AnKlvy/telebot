from student.handlers.main import show_student_main_menu
from curator.handlers.main import show_curator_main_menu
from teacher.handlers.main import show_teacher_main_menu
from manager.handlers.main import show_manager_main_menu
from admin.handlers.main import show_admin_main_menu
from common.navigation import navigation_manager

# Импортируем словари переходов и обработчиков
from student.states.states_homework import STATE_TRANSITIONS as STUDENT_TRANSITIONS, STATE_HANDLERS as STUDENT_HANDLERS
from curator.states.states_homework import STATE_TRANSITIONS as CURATOR_TRANSITIONS, STATE_HANDLERS as CURATOR_HANDLERS
from curator.states.states_analytics import STATE_TRANSITIONS as ANALYTICS_TRANSITIONS, STATE_HANDLERS as ANALYTICS_HANDLERS
from student.states.states_curator_contact import STATE_TRANSITIONS as CURATOR_CONTACT_TRANSITIONS, STATE_HANDLERS as CURATOR_CONTACT_HANDLERS
from student.states.states_progress import STATE_TRANSITIONS as PROGRESS_TRANSITIONS, STATE_HANDLERS as PROGRESS_HANDLERS
from student.states.states_shop import STATE_TRANSITIONS as SHOP_TRANSITIONS, STATE_HANDLERS as SHOP_HANDLERS

from student.states.states_account import STATE_TRANSITIONS as ACCOUNT_TRANSITIONS, STATE_HANDLERS as ACCOUNT_HANDLERS
from student.states.states_trial_ent import STATE_TRANSITIONS as TRIAL_ENT_TRANSITIONS, STATE_HANDLERS as TRIAL_ENT_HANDLERS
from student.states.states_quiz import STATE_TRANSITIONS as QUIZ_TRANSITIONS, STATE_HANDLERS as QUIZ_HANDLERS
from common.student_tests.transitions import STATE_TRANSITIONS as STUDENT_TESTS_TRANSITIONS, STATE_HANDLERS as STUDENT_TESTS_HANDLERS
from curator.states.states_groups import STATE_TRANSITIONS as GROUPS_TRANSITIONS, STATE_HANDLERS as GROUPS_HANDLERS
from curator.states.states_tests import STATE_TRANSITIONS as TESTS_TRANSITIONS, STATE_HANDLERS as TESTS_HANDLERS

# Импортируем словари переходов и обработчиков для преподавателя
from teacher.states.states_groups import STATE_TRANSITIONS as TEACHER_GROUPS_TRANSITIONS, STATE_HANDLERS as TEACHER_GROUPS_HANDLERS
from teacher.states.states_analytics import STATE_TRANSITIONS as TEACHER_ANALYTICS_TRANSITIONS, STATE_HANDLERS as TEACHER_ANALYTICS_HANDLERS
from teacher.states.states_tests import STATE_TRANSITIONS as TEACHER_TESTS_TRANSITIONS, STATE_HANDLERS as TEACHER_TESTS_HANDLERS

# Импортируем словари переходов и обработчиков для менеджера
from manager.states.states_analytics import STATE_TRANSITIONS as MANAGER_ANALYTICS_TRANSITIONS, STATE_HANDLERS as MANAGER_ANALYTICS_HANDLERS
from manager.states.states_homework import STATE_TRANSITIONS as MANAGER_HOMEWORK_TRANSITIONS, STATE_HANDLERS as MANAGER_HOMEWORK_HANDLERS
from manager.states.states_topics import STATE_TRANSITIONS as MANAGER_TOPICS_TRANSITIONS, STATE_HANDLERS as MANAGER_TOPICS_HANDLERS
from manager.states.states_lessons import STATE_TRANSITIONS as MANAGER_LESSONS_TRANSITIONS, STATE_HANDLERS as MANAGER_LESSONS_HANDLERS
from manager.states.states_bonus_tasks import STATE_TRANSITIONS as MANAGER_BONUS_TASKS_TRANSITIONS, STATE_HANDLERS as MANAGER_BONUS_TASKS_HANDLERS
from manager.states.states_month_tests import STATE_TRANSITIONS as MANAGER_MONTH_TESTS_TRANSITIONS, STATE_HANDLERS as MANAGER_MONTH_TESTS_HANDLERS
from admin.states.states_main import STATE_TRANSITIONS as ADMIN_TRANSITIONS, STATE_HANDLERS as ADMIN_HANDLERS
from admin.states.states_subjects import STATE_TRANSITIONS as ADMIN_SUBJECTS_TRANSITIONS, STATE_HANDLERS as ADMIN_SUBJECTS_HANDLERS

def register_handlers():
    """Регистрация всех обработчиков и переходов"""
    # Объединяем словари переходов и обработчиков для куратора
    curator_transitions = {**CURATOR_TRANSITIONS, **ANALYTICS_TRANSITIONS, **GROUPS_TRANSITIONS, **TESTS_TRANSITIONS}
    curator_handlers = {**CURATOR_HANDLERS, **ANALYTICS_HANDLERS, **GROUPS_HANDLERS, **TESTS_HANDLERS}

    # Объединяем словари переходов и обработчиков для студента
    student_transitions = {**STUDENT_TRANSITIONS, **CURATOR_CONTACT_TRANSITIONS, **PROGRESS_TRANSITIONS, **SHOP_TRANSITIONS, **ACCOUNT_TRANSITIONS, **TRIAL_ENT_TRANSITIONS, **QUIZ_TRANSITIONS, **STUDENT_TESTS_TRANSITIONS}
    student_handlers = {**STUDENT_HANDLERS, **CURATOR_CONTACT_HANDLERS, **PROGRESS_HANDLERS, **SHOP_HANDLERS, **ACCOUNT_HANDLERS, **TRIAL_ENT_HANDLERS, **QUIZ_HANDLERS, **STUDENT_TESTS_HANDLERS}

    # Объединяем словари переходов и обработчиков для преподавателя
    teacher_transitions = {**TEACHER_GROUPS_TRANSITIONS, **TEACHER_ANALYTICS_TRANSITIONS, **TEACHER_TESTS_TRANSITIONS}
    teacher_handlers = {**TEACHER_GROUPS_HANDLERS, **TEACHER_ANALYTICS_HANDLERS, **TEACHER_TESTS_HANDLERS}
    
    # Объединяем словари переходов и обработчиков для менеджера
    manager_transitions = {**MANAGER_ANALYTICS_TRANSITIONS, **MANAGER_HOMEWORK_TRANSITIONS, **MANAGER_TOPICS_TRANSITIONS, **MANAGER_LESSONS_TRANSITIONS, **MANAGER_BONUS_TASKS_TRANSITIONS, **MANAGER_MONTH_TESTS_TRANSITIONS}
    manager_handlers = {**MANAGER_ANALYTICS_HANDLERS, **MANAGER_HOMEWORK_HANDLERS, **MANAGER_TOPICS_HANDLERS, **MANAGER_LESSONS_HANDLERS, **MANAGER_BONUS_TASKS_HANDLERS, **MANAGER_MONTH_TESTS_HANDLERS}

    # Объединяем словари переходов и обработчиков для админа
    admin_transitions = {**ADMIN_TRANSITIONS, **ADMIN_SUBJECTS_TRANSITIONS}
    admin_handlers = {**ADMIN_HANDLERS, **ADMIN_SUBJECTS_HANDLERS}

    navigation_manager.register_role("student", student_transitions, {None: show_student_main_menu, **student_handlers})
    navigation_manager.register_role("curator", curator_transitions, {None: show_curator_main_menu, **curator_handlers})
    navigation_manager.register_role("teacher", teacher_transitions, {None: show_teacher_main_menu, **teacher_handlers})
    navigation_manager.register_role("manager", manager_transitions, {None: show_manager_main_menu, **manager_handlers})
    navigation_manager.register_role("admin", admin_transitions, {None: show_admin_main_menu, **admin_handlers})

    # Регистрируем обработчики для новых пользователей (по умолчанию показываем меню студента)
    navigation_manager.register_role("new_user", {}, {None: show_student_main_menu})
