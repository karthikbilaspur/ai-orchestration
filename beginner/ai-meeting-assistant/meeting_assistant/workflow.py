"""Workflow: parses the transcript, runs the agents and writes the outputs."""
from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

from meeting_assistant.agents.decisions import DecisionExtractorAgent
from meeting_assistant.agents.email import FollowUpEmailAgent
from meeting_assistant.agents.summarizer import SummarizerAgent
from meeting_assistant.agents.tasks import TaskAssignmentAgent
from meeting_assistant.models import MeetingInput, ValidationError
from meeting_assistant.parser import name_aliases, parse_transcript, participant_stats
from meeting_assistant.render import render_minutes_markdown
from meeting_assistant.storage import save_json, save_text

log = logging.getLogger(__name__)

MINUTES_JSON = "meeting_minutes.json"
MINUTES_MD = "meeting_minutes.md"
EMAIL_MD = "follow_up_email.md"


class MeetingWorkflow:
    def __init__(self, output_dir="."):
        self.output_dir = Path(output_dir)
        self.summarizer = SummarizerAgent()
        self.decisions = DecisionExtractorAgent()
        self.tasks = TaskAssignmentAgent()
        self.email = FollowUpEmailAgent()

    def run(self, meeting: MeetingInput) -> dict:
        sentences = parse_transcript(meeting.transcript, meeting.attendees)
        if not sentences:
            raise ValidationError("Transcript contains no usable text.")
        log.info("Parsed transcript: %d sentence(s)", len(sentences))
        log.info("Handoff: transcript -> summarizer")
        summary = self.summarizer.summarize(sentences, meeting.detail)
        key_topics = self.summarizer.key_topics(sentences)
        log.info("Handoff: summarizer -> decision extractor")
        decisions = self.decisions.extract(sentences)
        log.info("Handoff: decisions -> task assignment")
        tasks = self.tasks.extract(sentences, meeting.attendees, meeting.assign_tasks, meeting.reference_date)
        participants = participant_stats(sentences)

        report = {
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "meeting": {"topic": meeting.topic, "date": meeting.meeting_date, "organizer": meeting.organizer,
                        "attendees": meeting.attendees, "detail": meeting.detail},
            "summary": summary, "key_topics": key_topics, "decisions": decisions, "action_items": tasks,
            "participants": participants,
            "stats": {"sentences": len(sentences), "words": sum(len(s["text"].split()) for s in sentences),
                      "decisions": len(decisions), "action_items": len(tasks)},
            "warnings": self._warnings(meeting, sentences, decisions, tasks, participants),
        }
        files = [MINUTES_JSON, MINUTES_MD]
        if meeting.make_email:
            log.info("Handoff: task assignment -> follow-up email")
            report["follow_up_email"] = self.email.draft(
                meeting.topic, summary, decisions, tasks, meeting.attendees, meeting.organizer, meeting.meeting_date)
            files.append(EMAIL_MD)
        report["output_files"] = files

        save_json(self.output_dir / MINUTES_JSON, report)
        save_text(self.output_dir / MINUTES_MD, render_minutes_markdown(report))
        if meeting.make_email:
            save_text(self.output_dir / EMAIL_MD, report["follow_up_email"])
        log.info("Meeting minutes saved to %s", self.output_dir)
        return report

    @staticmethod
    def _warnings(meeting, sentences, decisions, tasks, participants) -> list:
        warnings = []
        if not participants:
            warnings.append("No speaker labels found; first-person commitments ('I will...') cannot be attributed.")
        aliases = name_aliases(meeting.attendees)
        unlisted = sorted(n for n in participants if meeting.attendees and n.lower() not in aliases)
        if unlisted:
            warnings.append("Speakers not in the attendee list: " + ", ".join(unlisted) + ".")
        if meeting.assign_tasks and not meeting.attendees:
            warnings.append("Task assignment was requested but no attendees were listed.")
        if not decisions:
            warnings.append("No decisions were detected.")
        if not tasks:
            warnings.append("No action items were detected.")
        elif meeting.assign_tasks and any(t["owner"] == "Unassigned" for t in tasks):
            warnings.append("Some action items have no clear owner.")
        return warnings
