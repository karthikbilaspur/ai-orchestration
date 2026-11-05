"""Write cheat-sheets to disk."""
import re
from pathlib import Path
import config


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", (text or "meeting").lower()).strip("-")


def write_single(state, out_dir=config.OUTPUT_DIR) -> Path:
    out_dir = Path(out_dir)
    out_dir.mkdir(exist_ok=True)
    path = out_dir / "meeting_brief.md"
    path.write_text(state.brief + "\n", encoding="utf-8")
    return path


def write_day(states, out_dir=config.OUTPUT_DIR / "day") -> Path:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = ["# Your day: back-to-back meetings", "", "| Time | With | Topic |", "|---|---|---|"]
    for s in states:
        rows.append(f"| {s.time_label or 'TBC'} | {s.company or '?'} | {s.topic or 'general'} |")
    parts = ["\n".join(rows)]
    for i, s in enumerate(states, 1):
        (out_dir / f"brief_{i:02d}_{slug(s.company)}_{slug(s.time_label)}.md").write_text(
            s.brief + "\n", encoding="utf-8")
        parts.append(s.brief)
    path = out_dir / "day_schedule.md"
    path.write_text("\n\n---\n\n".join(parts) + "\n", encoding="utf-8")
    return path
