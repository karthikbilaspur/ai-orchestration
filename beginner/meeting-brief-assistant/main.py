"""Entry point.

Usage:
  python main.py                                  # the task example
  python main.py --request "Meeting with X team at 3 PM about Y"
  python main.py --file sample_requests.txt       # back-to-back meetings, sorted by time
"""
import argparse
from pathlib import Path

import writer
from orchestrator import MeetingOrchestrator

MAIN_REQUEST = "I have a meeting with Flipkart team at 2 PM about AI integration"


def show_timing(state) -> None:
    seq = sum(state.timings.values())
    print(f"\n[Agents A and B ran in parallel: {state.wall_time:.2f}s "
          f"instead of {seq:.2f}s one after the other]")
    for err in state.errors:
        print("[note]", err)


def main() -> None:
    parser = argparse.ArgumentParser(description="Personal meeting assistant")
    parser.add_argument("--request", help="one meeting request")
    parser.add_argument("--file", help="text file with one meeting request per line")
    args = parser.parse_args()

    bot = MeetingOrchestrator()
    if args.file:
        lines = Path(args.file).read_text(encoding="utf-8").splitlines()
        states = bot.brief_day(lines)
        path = writer.write_day(states)
        print("\n" + "=" * 70 + "\nYOUR DAY (sorted by time)")
        for s in states:
            print(f"  {s.time_label or 'TBC':<9} {s.company or '?':<10} {s.topic or 'general discussion'}")
        print(f"\nBriefs saved in {path.parent}/ (open day_schedule.md for all of them).")
        return

    state = bot.brief(args.request or MAIN_REQUEST)
    path = writer.write_single(state)
    print("\n" + "=" * 70 + "\n" + state.brief)
    show_timing(state)
    print(f"\nSaved to {path}")


if __name__ == "__main__":
    main()
