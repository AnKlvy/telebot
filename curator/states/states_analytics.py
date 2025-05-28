from common.analytics.get_transitions_handlers import get_transitions_handlers
from curator.handlers.analytics import (
    CuratorAnalyticsStates,
)

STATE_TRANSITIONS, STATE_HANDLERS = get_transitions_handlers(CuratorAnalyticsStates, 'curator')