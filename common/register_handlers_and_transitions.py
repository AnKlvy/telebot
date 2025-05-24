from student.handlers.main import show_student_main_menu
from curator.handlers.main import show_curator_main_menu

# Импортируем словари переходов и обработчиков
from student.states.states_homework import STATE_TRANSITIONS as STUDENT_TRANSITIONS, STATE_HANDLERS as STUDENT_HANDLERS
from curator.states.states_homework import STATE_TRANSITIONS as CURATOR_TRANSITIONS, STATE_HANDLERS as CURATOR_HANDLERS
from curator.states.states_analytics import STATE_TRANSITIONS as ANALYTICS_TRANSITIONS, STATE_HANDLERS as ANALYTICS_HANDLERS
from student.states.states_curator_contact import STATE_TRANSITIONS as CURATOR_CONTACT_TRANSITIONS, STATE_HANDLERS as CURATOR_CONTACT_HANDLERS
from student.states.states_progress import STATE_TRANSITIONS as PROGRESS_TRANSITIONS, STATE_HANDLERS as PROGRESS_HANDLERS
from student.states.states_shop import STATE_TRANSITIONS as SHOP_TRANSITIONS, STATE_HANDLERS as SHOP_HANDLERS
from student.states.states_test_report import STATE_TRANSITIONS as TEST_REPORT_TRANSITIONS, STATE_HANDLERS as TEST_REPORT_HANDLERS
from student.states.states_account import STATE_TRANSITIONS as ACCOUNT_TRANSITIONS, STATE_HANDLERS as ACCOUNT_HANDLERS

# Импортируем менеджер навигации
from common.navigation import navigation_manager

def register_handlers():
    """Регистрация обработчиков для разных ролей"""
    # Объединяем словари переходов и обработчиков для куратора
    curator_transitions = {**CURATOR_TRANSITIONS, **ANALYTICS_TRANSITIONS}
    curator_handlers = {**CURATOR_HANDLERS, **ANALYTICS_HANDLERS}

    # Объединяем словари переходов и обработчиков для студента
    student_transitions = {**STUDENT_TRANSITIONS, **CURATOR_CONTACT_TRANSITIONS, **PROGRESS_TRANSITIONS, **SHOP_TRANSITIONS, **TEST_REPORT_TRANSITIONS, **ACCOUNT_TRANSITIONS}
    student_handlers = {**STUDENT_HANDLERS, **CURATOR_CONTACT_HANDLERS, **PROGRESS_HANDLERS, **SHOP_HANDLERS, **TEST_REPORT_HANDLERS, **ACCOUNT_HANDLERS}

    navigation_manager.register_role("student", student_transitions, {None: show_student_main_menu, **student_handlers})
    navigation_manager.register_role("curator", curator_transitions, {None: show_curator_main_menu, **curator_handlers})