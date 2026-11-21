"""Command-line interface: plan, show, done, undo, status."""
from __future__ import annotations

import argparse
import json
import logging
from datetime import date
from pathlib import Path

from study_planner.agents.collector import RequirementCollector
from study_planner.logging_setup import setup_logging, teardown_logging
from study_planner.models import ASSESSMENTS, LEVELS, ValidationError
from study_planner.storage import StorageError
from study_planner.workflow import StudyPlannerWorkflow

log = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="study-planner", description="AI Personal Study Planner")
    p.add_argument("--data-dir", default=".", help="folder for study_plan.json, progress.json, log.txt")
    sub = p.add_subparsers(dest="command")

    plan = sub.add_parser("plan", help="create a plan (interactive unless flags or --from-json are given)")
    plan.add_argument("--from-json", metavar="FILE", help="read requirements from a JSON file")
    plan.add_argument("--subject")
    plan.add_argument("--level", choices=LEVELS)
    plan.add_argument("--deadline", metavar="YYYY-MM-DD")
    plan.add_argument("--hours", type=float, help="study hours per day")
    plan.add_argument("--difficult", default="", help="comma-separated difficult topics")
    plan.add_argument("--assessment", choices=ASSESSMENTS)
    plan.add_argument("--start-date", metavar="YYYY-MM-DD")

    show = sub.add_parser("show", help="show overdue and upcoming sessions")
    show.add_argument("--days", type=int, default=7)
    done = sub.add_parser("done", help="mark sessions as completed")
    done.add_argument("indices", type=int, nargs="+")
    undo = sub.add_parser("undo", help="mark sessions as not completed")
    undo.add_argument("indices", type=int, nargs="+")
    sub.add_parser("status", help="show progress summary")
    return p


def format_report(report: dict, rows: int = 14, questions: int = 5) -> str:
    out = ["", "TOPIC PRIORITIES"]
    out += [f"- {t['topic']}: {t['priority']}" for t in report["topic_priorities"]]
    sched = report["daily_schedule"]
    out += ["", f"DAILY PLAN ({len(sched)} days)"]
    out += [f"[{s['index']}] {s['day']} | {s['topic']} | {s['hours']}h | {s['activity']}" for s in sched[:rows]]
    if len(sched) > rows:
        out.append(f"... {len(sched) - rows} more days in study_plan.json")
    qs = report["practice_questions"]
    out += ["", f"PRACTICE QUESTIONS ({len(qs)} total)"]
    out += [f"- {q['question']}" for q in qs[:questions]]
    s = report["summary"]
    out += ["", f"Total: {s['total_hours']}h over {s['total_days']} days "
                f"({s['study_sessions']} study, {s['assessment_sessions']} assessment, "
                f"{s['revision_sessions']} revision).",
            "Saved study_plan.json. Track progress with: python main.py done <session numbers>"]
    return "\n".join(out)


def format_status(p: dict) -> str:
    lines = [f"Progress: {p['completed']}/{p['total']} sessions ({p['completion_percent']}%) - {p['status']}",
             f"Hours: {p['hours_completed']}/{p['hours_total']}  Streak: {p['streak_days']} day(s)"]
    if p["overdue_sessions"]:
        lines.append("Overdue sessions: " + ", ".join(map(str, p["overdue_sessions"])))
    if p["next_session"] is not None:
        lines.append(f"Next session: {p['next_session']}")
    return "\n".join(lines)


def _requirements_from_args(args, collector, input_fn):
    if args.from_json:
        try:
            data = json.loads(Path(args.from_json).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValidationError(f"Could not read {args.from_json}: {exc}") from exc
        return collector.from_dict(data)
    flags = {"subject": args.subject, "level": args.level, "deadline": args.deadline,
             "hours": args.hours, "assessment": args.assessment}
    if any(v is not None for v in flags.values()):
        missing = [k for k, v in flags.items() if v is None]
        if missing:
            raise ValidationError("Missing flag(s): " + ", ".join("--" + m for m in missing))
        return collector.from_dict({**flags, "difficult_topics": args.difficult, "start_date": args.start_date})
    return collector.collect(input_fn)


def main(argv=None, input_fn=input, output_fn=print, today: date | None = None) -> int:
    args = build_parser().parse_args(argv)
    handler = setup_logging(Path(args.data_dir) / "log.txt")
    try:
        workflow = StudyPlannerWorkflow(args.data_dir, today=today)
        command = args.command or "plan"
        if command == "plan":
            if args.command is None:
                args.from_json = args.subject = args.level = args.deadline = args.hours = None
                args.assessment = args.start_date = None
            collector = RequirementCollector(output_fn=output_fn, today=today)
            report = workflow.run(_requirements_from_args(args, collector, input_fn))
            output_fn(format_report(report))
        elif command == "show":
            result = workflow.upcoming(args.days)
            for title, key in (("OVERDUE", "overdue"), ("UPCOMING", "upcoming")):
                output_fn(f"{title}:")
                rows = result[key] or []
                for s in rows:
                    output_fn(f"  [{s['index']}] {s['day']} | {s['topic']} | {s['hours']}h | {s['activity']}")
                if not rows:
                    output_fn("  (none)")
        elif command in ("done", "undo"):
            fn = workflow.mark_done if command == "done" else workflow.mark_undone
            output_fn(format_status(fn(args.indices)))
        elif command == "status":
            output_fn(format_status(workflow.status()))
        return 0
    except (ValidationError, StorageError) as exc:
        log.error("%s", exc)
        output_fn(f"Error: {exc}")
        return 1
    finally:
        teardown_logging(handler)
