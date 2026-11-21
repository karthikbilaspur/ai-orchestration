"""Input model and validators for the meeting assistant."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

DETAILS = ("short", "detailed")
MAX_TOPIC_LEN = 120
MAX_TRANSCRIPT_CHARS = 500_000


class ValidationError(ValueError):
    """Raised when user-supplied input is invalid."""


def parse_date(value, field_name: str = "date") -> date:
    try:
        return date.fromisoformat(str(value).strip())
    except ValueError:
        raise ValidationError(
            f"{field_name} must be a valid date in YYYY-MM-DD format, got {value!r}."
        ) from None


def validate_topic(value) -> str:
    topic = " ".join(str(value).split())
    if not topic:
        raise ValidationError("Meeting topic cannot be empty.")
    if len(topic) > MAX_TOPIC_LEN:
        raise ValidationError(f"Meeting topic must be at most {MAX_TOPIC_LEN} characters.")
    return topic


def validate_detail(value) -> str:
    detail = str(value).strip().lower() or "short"
    if detail not in DETAILS:
        raise ValidationError(f"Summary length must be one of: {', '.join(DETAILS)}.")
    return detail


def validate_transcript(value) -> str:
    text = str(value or "").replace("\r\n", "\n").replace("\r", "\n").strip()
    if not text:
        raise ValidationError("Transcript is empty.")
    if len(text) > MAX_TRANSCRIPT_CHARS:
        raise ValidationError(f"Transcript is too long (limit {MAX_TRANSCRIPT_CHARS} characters).")
    return text


def parse_attendees(value) -> list:
    """Accept a comma/newline separated string or an iterable; return a de-duplicated list."""
    if value is None:
        return []
    items = value.replace("\n", ",").split(",") if isinstance(value, str) else list(value)
    seen, result = set(), []
    for item in items:
        name = " ".join(str(item).split())
        if name and name.lower() not in seen:
            seen.add(name.lower())
            result.append(name)
    return result


def parse_bool(value, default: bool | None = None) -> bool:
    text = str(value).strip().lower()
    if not text and default is not None:
        return default
    if text in {"y", "yes", "true", "1"}:
        return True
    if text in {"n", "no", "false", "0"}:
        return False
    raise ValidationError("Please answer yes or no.")


@dataclass
class MeetingInput:
    topic: str
    transcript: str
    attendees: list = field(default_factory=list)
    detail: str = "short"
    assign_tasks: bool = False
    make_email: bool = True
    organizer: str = "Meeting Organizer"
    meeting_date: str = ""

    def __post_init__(self):
        self.topic = validate_topic(self.topic)
        self.transcript = validate_transcript(self.transcript)
        self.attendees = parse_attendees(self.attendees)
        self.detail = validate_detail(self.detail)
        self.assign_tasks = bool(self.assign_tasks)
        self.make_email = bool(self.make_email)
        self.organizer = " ".join(str(self.organizer).split()) or "Meeting Organizer"
        self.meeting_date = (
            parse_date(self.meeting_date, "Meeting date") if self.meeting_date else date.today()
        ).isoformat()

    @property
    def reference_date(self) -> date:
        return date.fromisoformat(self.meeting_date)
