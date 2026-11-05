"""Turn 'I have a meeting with Flipkart team at 2 PM about AI integration' into fields."""
import re
from state import MeetingState

_TIME = re.compile(r"\b(\d{1,2})(?::(\d{2}))?\s*([ap])\.?m\.?(?![a-z])", re.I)
_COMPANY = re.compile(
    r"\bwith\s+(?:the\s+)?(?P<c>[A-Za-z0-9&.\-' ]+?)"
    r"(?:\s+(?:team|folks|people|group|guys))?\s*"
    r"(?=\bat\b|\babout\b|\bregarding\b|\bon\b|\bfor\b|$)", re.I)
_TOPIC = re.compile(r"\b(?:about|regarding)\s+(.+?)\s*[.!?]*$", re.I)
_AI = re.compile(r"(?<![a-z])(ai|llms?|ml|genai|machine learning|artificial intelligence|gpt|chatbot)(?![a-z])", re.I)


def parse_request(text: str) -> MeetingState:
    state = MeetingState(request=text.strip())

    t = _TIME.search(text)
    if t:
        hour, minute, ap = int(t.group(1)), int(t.group(2) or 0), t.group(3).lower()
        state.time_minutes = ((hour % 12) + (12 if ap == "p" else 0)) * 60 + minute
        state.time_label = f"{hour}{':%02d' % minute if t.group(2) else ''} {'PM' if ap == 'p' else 'AM'}"
    else:
        state.errors.append("no meeting time found")

    c = _COMPANY.search(text)
    if c and c.group("c").strip():
        state.company = c.group("c").strip(" .,-")
    else:
        state.errors.append("no company/team name found")

    m = _TOPIC.search(text)
    if m:
        state.topic = m.group(1).strip()
        state.category = "ai_integration" if _AI.search(state.topic) else "generic"
    else:
        state.errors.append("no topic found")
    return state
