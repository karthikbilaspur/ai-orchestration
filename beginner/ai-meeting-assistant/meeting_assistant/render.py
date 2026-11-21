"""Rendering helpers: Markdown minutes and console output."""
from __future__ import annotations


def _cell(value) -> str:
    return str(value if value not in (None, "") else "-").replace("|", "\\|").replace("\n", " ")


def render_minutes_markdown(report: dict) -> str:
    m = report["meeting"]
    out = [f"# Meeting Minutes: {m['topic']}", "",
           f"**Date:** {m['date']}  ", f"**Organizer:** {m['organizer']}  ",
           f"**Attendees:** {', '.join(m['attendees']) or 'not listed'}", "",
           "## Summary", "", report["summary"], ""]
    if report["key_topics"]:
        out += ["## Key topics", "", ", ".join(report["key_topics"]), ""]
    out += ["## Decisions", ""]
    out += [f"{i}. {d['text']}" for i, d in enumerate(report["decisions"], 1)] or ["_None detected._"]
    out += ["", "## Action items", ""]
    if report["action_items"]:
        out += ["| ID | Task | Owner | Due | Priority |", "|----|------|-------|-----|----------|"]
        for t in report["action_items"]:
            out.append(f"| {t['id']} | {_cell(t['task'])} | {_cell(t['owner'])} | "
                       f"{_cell(t['due_date'] or t['due_text'])} | {t['priority']} |")
    else:
        out.append("_None detected._")
    if report["participants"]:
        out += ["", "## Participation", ""]
        out += [f"- {name}: {v['sentences']} sentence(s), {v['words']} words"
                for name, v in sorted(report["participants"].items())]
    if report["warnings"]:
        out += ["", "## Review notes", ""] + [f"- {w}" for w in report["warnings"]]
    out += ["", "_Generated heuristically; please review before sharing._", ""]
    return "\n".join(out)


def render_console(report: dict) -> str:
    out = ["", "SUMMARY", report["summary"]]
    if report["key_topics"]:
        out += ["", "KEY TOPICS", ", ".join(report["key_topics"])]
    out += ["", "DECISIONS"] + ([f"- {d['text']}" for d in report["decisions"]] or ["- (none detected)"])
    out += ["", "ACTION ITEMS"]
    for t in report["action_items"]:
        due = t["due_date"] or t["due_text"] or "no deadline"
        out.append(f"- [{t['id']}] {t['task']} | {t['owner']} | {due} | {t['priority']}")
    if not report["action_items"]:
        out.append("- (none detected)")
    if report["warnings"]:
        out += ["", "REVIEW NOTES"] + [f"- {w}" for w in report["warnings"]]
    out += ["", "Saved: " + ", ".join(report["output_files"])]
    return "\n".join(out)
