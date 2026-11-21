from datetime import date
from pathlib import Path

from meeting_assistant.models import MeetingInput

TODAY = date(2026, 11, 21)  # a Saturday
SAMPLE = (Path(__file__).resolve().parent.parent / "sample_transcript.txt").read_text(encoding="utf-8")
ATTENDEES = ["Maya Rao", "Sam Lee", "Priya Nair"]


def make_meeting(**kw):
    data = dict(topic="Q4 Launch Sync", transcript=SAMPLE, attendees=ATTENDEES, detail="short",
                assign_tasks=True, make_email=True, meeting_date="2026-11-21")
    data.update(kw)
    return MeetingInput(**data)
