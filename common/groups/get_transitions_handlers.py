from common.groups.handlers import (
    show_groups, show_group_students, show_student_profile
)

def get_transitions_handlers(states_group, role):
    """
    Создает словари переходов и обработчиков для работы с группами

    Args:
        states_group: Группа состояний (CuratorGroupStates или TeacherGroupStates)
        role: Роль пользователя ('curator' или 'teacher')

    Returns:
        tuple: (STATE_TRANSITIONS, STATE_HANDLERS) - словари переходов и обработчиков
    """
    # Словарь переходов между состояниями
    STATE_TRANSITIONS = {
        states_group.select_group: None,  # None означает возврат в главное меню
        states_group.select_student: states_group.select_group,
        states_group.student_profile: states_group.select_student
    }

    # Словарь обработчиков для каждого состояния
    STATE_HANDLERS = {
        states_group.select_group: lambda callback, state: show_groups(callback, state, role),
        states_group.select_student: lambda callback, state: show_group_students(callback, state, role),
        states_group.student_profile: lambda callback, state: show_student_profile(callback, state, role)
    }

    return STATE_TRANSITIONS, STATE_HANDLERS 