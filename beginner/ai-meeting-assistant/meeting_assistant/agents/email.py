"""Follow-up Email agent: drafts a recap email grouped by owner."""
from __future__ import annotations

import logging

log = logging.getLogger(__name__)


def _text(item) -> str:
    return item["text"] if isinstance(item, dict) else str(item)


class FollowUpEmailAgent:
    def draft(self, topic, summary, decisions, tasks, attendees=None, organizer="Meeting Organizer",
              meeting_date=None) -> str:
        subject = f"Subject: Follow-up: {topic}" + (f" ({meeting_date})" if meeting_date else "")
        lines = [subject]
        if attendees:
            lines.append("To: " + ", ".join(attendees))
        lines += ["", "Hi everyone,", "", "Thanks for joining. Here is a recap of our discussion:", "", summary, ""]
        lines += ["Decisions:"] + ([f"- {_text(d)}" for d in decisions] or ["- No formal decisions were recorded."]) + [""]
        lines.append("Action items:")
        if tasks:
            for t in tasks:
                due = f" | Due: {t['due_date'] or t['due_text']}" if (t.get("due_date") or t.get("due_text")) else ""
                flag = " | Priority: high" if t.get("priority") == "high" else ""
                lines.append(f"- {t['task']} (Owner: {t['owner']}{due}{flag})")
        else:
            lines.append("- No action items were recorded.")
        lines += ["", "Please reply if anything needs correcting.", "", "Best,", organizer]
        return "\n".join(lines)
