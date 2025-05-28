from common.analytics.get_transitions_handlers import get_transitions_handlers
from teacher.handlers.analytics import TeacherAnalyticsStates

# Словарь переходов между состояниями
STATE_TRANSITIONS, STATE_HANDLERS = get_transitions_handlers(TeacherAnalyticsStates, 'teacher')