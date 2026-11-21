"""Deadline phrase detection and resolution relative to the meeting date."""
from __future__ import annotations

import re
from calendar import monthrange
from datetime import date, timedelta

WEEKDAYS = {"monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3, "friday": 4,
            "saturday": 5, "sunday": 6}

_ISO = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")
_IN_N = re.compile(r"\bin\s+(\d{1,3})\s+(day|week)s?\b", re.IGNORECASE)
_WEEKDAY = re.compile(r"\b(?:(next|this|coming)\s+)?(" + "|".join(WEEKDAYS) + r")\b", re.IGNORECASE)
_RELATIVE = (
    (re.compile(r"\btomorrow\b", re.IGNORECASE), lambda ref: ref + timedelta(days=1)),
    (re.compile(r"\b(?:today|tonight|eod|end of (?:the )?day)\b", re.IGNORECASE), lambda ref: ref),
    (re.compile(r"\bnext week\b", re.IGNORECASE), lambda ref: ref + timedelta(days=7)),
    (re.compile(r"\b(?:end of (?:the )?week|eow|this week)\b", re.IGNORECASE),
     lambda ref: ref + timedelta(days=(4 - ref.weekday()) % 7)),
    (re.compile(r"\b(?:end of (?:the )?month|eom)\b", re.IGNORECASE),
     lambda ref: ref.replace(day=monthrange(ref.year, ref.month)[1])),
    (re.compile(r"\bnext month\b", re.IGNORECASE), lambda ref: None),
)


def _weekday_date(ref: date, prefix: str | None, name: str) -> date:
    target = WEEKDAYS[name.lower()]
    delta = (target - ref.weekday()) % 7 or 7
    result = ref + timedelta(days=delta)
    if prefix and prefix.lower() == "next" and result.isocalendar()[:2] == ref.isocalendar()[:2]:
        result += timedelta(days=7)
    return result


def extract_deadline(text: str, ref: date):
    """Return ``(phrase, iso_date_or_None)`` for the first deadline phrase, else ``(None, None)``."""
    m = _ISO.search(text)
    if m:
        try:
            return m.group(1), date.fromisoformat(m.group(1)).isoformat()
        except ValueError:
            pass
    m = _IN_N.search(text)
    if m:
        days = int(m.group(1)) * (7 if m.group(2).lower() == "week" else 1)
        return m.group(0), (ref + timedelta(days=days)).isoformat()
    m = _WEEKDAY.search(text)
    if m:
        return m.group(0), _weekday_date(ref, m.group(1), m.group(2)).isoformat()
    for pattern, resolver in _RELATIVE:
        m = pattern.search(text)
        if m:
            resolved = resolver(ref)
            return m.group(0), resolved.isoformat() if resolved else None
    return None, None
