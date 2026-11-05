"""Orchestrator: runs the 4 agents in order, with error checks and human approval.

Usage:
    python main.py        # runs email number 0 from sample_emails.json
    python main.py 1      # runs email number 1
"""
import json
import sys
from datetime import datetime
from typing import Any, Callable, TypedDict, cast

from agents import classifier as classifier_module
from agents import email_reader as email_reader_module
from agents import problem_solver as problem_solver_module
from agents import reply_writer as reply_writer_module


class ClassificationOutput(TypedDict):
    confidence: float

CONFIDENCE_LIMIT = 0.7
RUN_LOG = "run_log.txt"


def log(title: str, data: Any):
    """Print a step and also save it to run_log.txt."""
    text = json.dumps(data, indent=2, ensure_ascii=False) if not isinstance(data, str) else data
    print(f"\n{title}\n{text}")
    with open(RUN_LOG, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {title}\n{text}\n\n")


def run_pipeline(email: str):
    log("=== NEW EMAIL ===", email)

    email_reader: Callable[[str], dict[str, Any]] = cast(
        Callable[[str], dict[str, Any]], email_reader_module.email_reader
    )
    a1 = email_reader(email)
    log("[1/4] Email Reader output", a1)

    a2 = cast(ClassificationOutput, classifier_module.classifier(a1))
    log("[2/4] Classifier output", a2)

    # Error check: stop if the Classifier is unsure
    if a2["confidence"] < CONFIDENCE_LIMIT:
        log("STOPPED", "Low classifier confidence. Sent to a human.")
        return

    a3 = problem_solver_module.problem_solver(a1, a2)
    log("[3/4] Problem Solver output", a3)

    reply_writer: Callable[
        [dict[str, Any], dict[str, Any]], dict[str, Any]
    ] = cast(
        Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]],
        reply_writer_module.reply_writer,
    )
    a4 = reply_writer(a1, a3)
    log("[4/4] Reply Writer draft", a4)

    print("\n----- DRAFT REPLY -----")
    print("SUBJECT:", a4["subject"])
    print()
    print(a4["body"])
    print("-----------------------")

    if a3.get("needs_human"):
        print("Note: Problem Solver flagged this case for human attention.")

    # Human approval step
    choice = input("\nSend this reply? (y/n): ").strip().lower()
    if choice == "y":
        log("HUMAN DECISION", "Approved. (Sending the email would happen here.)")
    else:
        log("HUMAN DECISION", "Rejected. Sent back for editing.")


if __name__ == "__main__":
    with open("sample_emails.json", encoding="utf-8") as f:
        emails = json.load(f)
    index = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    run_pipeline(emails[index])
