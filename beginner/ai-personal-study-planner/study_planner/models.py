"""Requirement model and input validators.

All validators raise :class:`ValidationError` with a human-readable message so
that both the interactive collector and the non-interactive CLI can report
problems consistently.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date

LEVELS = ("beginner", "intermediate", "advanced")
ASSESSMENTS = ("daily quizzes", "weekly assessments")
PRIORITIES = ("high", "medium", "low")
PRIORITY_WEIGHT = {"high": 3, "medium": 2, "low": 1}

MIN_HOURS = 0.25
MAX_HOURS = 16.0
MAX_SUBJECT_LEN = 100
MAX_PLAN_DAYS = 366


class ValidationError(ValueError):
    """Raised when user-supplied input is invalid."""


def parse_date(value, field_name: str = "date") -> date:
    try:
        return date.fromisoformat(str(value).strip())
    except ValueError:
        raise ValidationError(
            f"{field_name} must be a valid date in YYYY-MM-DD format, got {value!r}."
        ) from None


def validate_subject(value) -> str:
    subject = " ".join(str(value).split())
    if not subject:
        raise ValidationError("Subject cannot be empty.")
    if len(subject) > MAX_SUBJECT_LEN:
        raise ValidationError(f"Subject must be at most {MAX_SUBJECT_LEN} characters.")
    return subject


def validate_level(value) -> str:
    level = str(value).strip().lower()
    if level not in LEVELS:
        raise ValidationError(f"Level must be one of: {', '.join(LEVELS)}.")
    return level


def validate_hours(value) -> float:
    try:
        hours = float(value)
    except (TypeError, ValueError):
        raise ValidationError("Study hours per day must be a number.") from None
    if not (MIN_HOURS <= hours <= MAX_HOURS):
        raise ValidationError(f"Study hours per day must be between {MIN_HOURS} and {MAX_HOURS}.")
    return round(hours, 2)


def validate_assessment(value) -> str:
    assessment = " ".join(str(value).strip().lower().split())
    if assessment not in ASSESSMENTS:
        raise ValidationError(f"Assessment preference must be one of: {', '.join(ASSESSMENTS)}.")
    return assessment


def parse_topics(value) -> list:
    """Turn a comma-separated string (or iterable) into a de-duplicated topic list."""
    if value is None:
        return []
    items = value.split(",") if isinstance(value, str) else list(value)
    seen, result = set(), []
    for item in items:
        topic = " ".join(str(item).split())
        if topic and topic.lower() not in seen:
            seen.add(topic.lower())
            result.append(topic)
    return result


def validate_deadline(value, start: date) -> date:
    deadline = parse_date(value, "Deadline")
    if deadline < start:
        raise ValidationError(f"Deadline must be on or after the start date ({start.isoformat()}).")
    if (deadline - start).days + 1 > MAX_PLAN_DAYS:
        raise ValidationError(f"Deadline is too far away; plans are limited to {MAX_PLAN_DAYS} days.")
    return deadline


@dataclass
class StudyRequirements:
    subject: str
    level: str
    deadline: str
    hours_daily: float
    difficult_topics: list = field(default_factory=list)
    assessment: str = "daily quizzes"
    start_date: str = ""

    def __post_init__(self):
        self.subject = validate_subject(self.subject)
        self.level = validate_level(self.level)
        self.hours_daily = validate_hours(self.hours_daily)
        self.assessment = validate_assessment(self.assessment)
        self.difficult_topics = parse_topics(self.difficult_topics)
        start = parse_date(self.start_date, "Start date") if self.start_date else date.today()
        self.start_date = start.isoformat()
        self.deadline = validate_deadline(self.deadline, start).isoformat()

    @property
    def days_available(self) -> int:
        return (date.fromisoformat(self.deadline) - date.fromisoformat(self.start_date)).days + 1

    def to_dict(self) -> dict:
        return asdict(self)
