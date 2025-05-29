from curator.handlers.groups import CuratorGroupStates
from common.groups.get_transitions_handlers import get_transitions_handlers

# Создаем словари переходов и обработчиков для куратора
STATE_TRANSITIONS, STATE_HANDLERS = get_transitions_handlers(CuratorGroupStates, "curator")