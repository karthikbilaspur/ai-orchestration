"""Command-line interface. Anything not passed as a flag is asked interactively."""
from __future__ import annotations

import argparse
import logging
from datetime import date
from pathlib import Path

from meeting_assistant.logging_setup import setup_logging, teardown_logging
from meeting_assistant.models import (
    DETAILS, MAX_TRANSCRIPT_CHARS, MeetingInput, ValidationError, parse_attendees, parse_bool,
    parse_date, validate_detail, validate_topic,
)
from meeting_assistant.render import render_console
from meeting_assistant.storage import StorageError, read_text
from meeting_assistant.workflow import MeetingWorkflow

log = logging.getLogger(__name__)
MAX_ATTEMPTS = 5


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="meeting-assistant", description="AI Meeting Assistant")
    p.add_argument("--topic")
    p.add_argument("--attendees", help="comma-separated names")
    p.add_argument("--transcript-file", metavar="FILE", help="UTF-8 transcript file")
    p.add_argument("--detail", choices=DETAILS, help="summary length")
    p.add_argument("--assign-tasks", action=argparse.BooleanOptionalAction, default=None,
                   help="assign owners to action items (default: yes if attendees are given)")
    p.add_argument("--email", action=argparse.BooleanOptionalAction, default=None,
                   help="generate the follow-up email (default: yes)")
    p.add_argument("--organizer", default="Meeting Organizer", help="name used to sign the email")
    p.add_argument("--date", metavar="YYYY-MM-DD", help="meeting date (default: today)")
    p.add_argument("--output-dir", default=".", help="where outputs and log.txt are written")
    return p


def _ask(input_fn, output_fn, prompt, validator):
    for _ in range(MAX_ATTEMPTS):
        try:
            raw = input_fn(prompt)
        except EOFError:
            raise ValidationError("Input ended before all answers were collected.") from None
        try:
            return validator(raw)
        except ValidationError as exc:
            output_fn(f"  ! {exc}")
    raise ValidationError(f"Too many invalid answers for: {prompt.strip()}")


def _paste(input_fn, output_fn) -> str:
    output_fn("Paste transcript. Enter a line containing END when finished:")
    lines = []
    while True:
        try:
            line = input_fn("")
        except EOFError:
            break
        if line.strip() == "END":
            break
        lines.append(line)
    return "\n".join(lines)


def _gather(args, input_fn, output_fn, today: date) -> MeetingInput:
    topic = validate_topic(args.topic) if args.topic else _ask(input_fn, output_fn, "1. Meeting topic: ", validate_topic)
    non_interactive = bool(args.topic and args.transcript_file)
    attendees = parse_attendees(args.attendees) if args.attendees is not None else (
        [] if non_interactive else parse_attendees(input_fn("2. Attendees (comma-separated): ")))
    default_assign = bool(attendees)
    if args.assign_tasks is not None:
        assign = args.assign_tasks
    elif non_interactive:
        assign = default_assign
    else:
        assign = _ask(input_fn, output_fn, f"3. Assign tasks to named attendees? ({'Y/n' if default_assign else 'y/N'}): ",
                      lambda v: parse_bool(v, default_assign))
    if args.detail:
        detail = args.detail
    elif non_interactive:
        detail = "short"
    else:
        detail = _ask(input_fn, output_fn, "4. Summary length (short/detailed): ", validate_detail)
    if args.email is not None:
        make_email = args.email
    elif non_interactive:
        make_email = True
    else:
        make_email = _ask(input_fn, output_fn, "5. Generate follow-up email? (Y/n): ", lambda v: parse_bool(v, True))
    source = args.transcript_file or (None if non_interactive else
                                      input_fn("Transcript file path (leave blank to paste transcript): ").strip())
    transcript = read_text(source, MAX_TRANSCRIPT_CHARS) if source else _paste(input_fn, output_fn)
    meeting_date = parse_date(args.date, "Meeting date").isoformat() if args.date else today.isoformat()
    return MeetingInput(topic, transcript, attendees, detail, assign, make_email, args.organizer, meeting_date)


def main(argv=None, input_fn=input, output_fn=print, today: date | None = None) -> int:
    args = build_parser().parse_args(argv)
    handler = setup_logging(Path(args.output_dir) / "log.txt")
    try:
        meeting = _gather(args, input_fn, output_fn, today or date.today())
        report = MeetingWorkflow(args.output_dir).run(meeting)
        output_fn(render_console(report))
        return 0
    except (ValidationError, StorageError) as exc:
        log.error("%s", exc)
        output_fn(f"Error: {exc}")
        return 1
    finally:
        teardown_logging(handler)
