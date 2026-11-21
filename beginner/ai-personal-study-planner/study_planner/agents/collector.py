"""Requirement Collector agent: gathers and validates the six learner inputs."""
from __future__ import annotations

import logging
from datetime import date

from study_planner.models import (
    StudyRequirements,
    ValidationError,
    parse_date,
    parse_topics,
    validate_assessment,
    validate_deadline,
    validate_hours,
    validate_level,
    validate_subject,
)

log = logging.getLogger(__name__)


class RequirementCollector:
    def __init__(self, max_attempts: int = 5, output_fn=print, today: date | None = None):
        self.max_attempts = max_attempts
        self.output_fn = output_fn
        self.today = today

    def _start(self) -> date:
        return self.today or date.today()

    def _ask(self, input_fn, prompt, validator):
        for _ in range(self.max_attempts):
            try:
                raw = input_fn(prompt)
            except EOFError:
                raise ValidationError("Input ended before all answers were collected.") from None
            try:
                return validator(raw)
            except ValidationError as exc:
                self.output_fn(f"  ! {exc}")
        raise ValidationError(f"Too many invalid answers for: {prompt.strip()}")

    def collect(self, input_fn=input) -> StudyRequirements:
        """Interactively ask the six questions, re-prompting on invalid answers."""
        start = self._start()
        subject = self._ask(input_fn, "1. Subject to study: ", validate_subject)
        level = self._ask(input_fn, "2. Current level (beginner/intermediate/advanced): ", validate_level)
        deadline = self._ask(input_fn, "3. Deadline (YYYY-MM-DD): ", lambda v: validate_deadline(v, start))
        hours = self._ask(input_fn, "4. Study hours per day: ", validate_hours)
        difficult = parse_topics(input_fn("5. Most difficult topics (comma-separated, optional): "))
        assessment = self._ask(
            input_fn, "6. Assessment preference (daily quizzes/weekly assessments): ", validate_assessment
        )
        req = StudyRequirements(subject, level, deadline.isoformat(), hours, difficult, assessment, start.isoformat())
        log.info("Collected requirements: %s", req.to_dict())
        return req

    def from_dict(self, data: dict) -> StudyRequirements:
        """Build requirements from a mapping (used by --from-json and CLI flags)."""
        if not isinstance(data, dict):
            raise ValidationError("Requirements must be a JSON object.")
        hours = data.get("hours_daily", data.get("hours"))
        required = {"subject": data.get("subject"), "level": data.get("level"),
                    "deadline": data.get("deadline"), "hours_daily": hours}
        missing = [k for k, v in required.items() if v in (None, "")]
        if missing:
            raise ValidationError(f"Missing required field(s): {', '.join(missing)}.")
        start = data.get("start_date") or self._start().isoformat()
        parse_date(start, "Start date")
        req = StudyRequirements(
            subject=data["subject"], level=data["level"], deadline=data["deadline"],
            hours_daily=hours, difficult_topics=data.get("difficult_topics", []),
            assessment=data.get("assessment", "daily quizzes"), start_date=start,
        )
        log.info("Loaded requirements: %s", req.to_dict())
        return req
