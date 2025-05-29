from teacher.handlers.groups import TeacherGroupStates
from common.groups.get_transitions_handlers import get_transitions_handlers

# Создаем словари переходов и обработчиков для учителя
STATE_TRANSITIONS, STATE_HANDLERS = get_transitions_handlers(TeacherGroupStates, "teacher")