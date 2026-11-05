"""Agent 2: extract the order ID and look up tracking. Needs no LLM."""
import re
from state import ConversationState
from tools.tracking import get_tracking

ORDER_ID_PATTERN = re.compile(r"\b([A-Za-z]{2,6}\d{3,})\b")


class InfoAgent:
    def run(self, state: ConversationState) -> ConversationState:
        match = ORDER_ID_PATTERN.search(state.message)
        if match:
            state.order_id = match.group(1).upper()
            state.tracking = get_tracking(state.order_id)
        return state
