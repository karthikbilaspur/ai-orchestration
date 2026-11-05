"""Entry point.

Usage:
  python main.py                              # task example (Rohan) + all sample resumes
  python main.py --resume "..." [--jd "..."]  # screen one resume
  python main.py --batch sample_resumes.json  # screen a JSON list of resumes
  python main.py --resume-dir resumes/        # screen every .txt file in a folder
"""
import argparse
import json

import batch
import config
from orchestrator import ScreeningOrchestrator

MAIN_RESUME = ("Resume: Name: Rohan. Skills: Python, Excel. Project: Made a calculator app. "
               "No AI experience.")


def show_single(state) -> None:
    print("\n" + "=" * 70)
    print("OUTPUT   :", json.dumps(state.result()))
    print("Candidate:", state.candidate_name, "| skills:", state.skills, "| denied:", state.negated)
    print("Match    :", state.match_level, "| missing:", state.missing)
    if state.score is None:
        print("Scorer   : skipped (pipeline stopped at the Checker)")
    else:
        print("Score    :", f"{state.score}/10", state.score_breakdown)
        for line in state.reason_lines:
            print("  -", line)


def show_batch(rows) -> None:
    print("\n" + "=" * 70)
    print(f"{'ID':<6}{'Name':<10}{'Status':<13}{'Score':<7}Reason")
    for r in rows:
        score = "-" if r["score"] is None else r["score"]
        print(f"{r['id']:<6}{r['name']:<10}{r['status']:<13}{str(score):<7}{r['reason']}")
    print("\nSummary:", dict(batch.summarize(rows)))


def main() -> None:
    parser = argparse.ArgumentParser(description="Job application screener")
    parser.add_argument("--resume", help="resume text to screen")
    parser.add_argument("--jd", default=config.DEFAULT_JD, help="job description")
    parser.add_argument("--batch", help="JSON file with a list of resumes")
    parser.add_argument("--resume-dir", help="folder of .txt resumes")
    args = parser.parse_args()

    bot = ScreeningOrchestrator()
    if args.resume:
        show_single(bot.screen(args.resume, args.jd))
        return

    if args.batch or args.resume_dir:
        items = batch.load_json(args.batch) if args.batch else batch.load_dir(args.resume_dir)
    else:
        show_single(bot.screen(MAIN_RESUME, args.jd, "TASK"))
        items = batch.load_json(config.BASE_DIR / "sample_resumes.json")

    rows = batch.run_batch(bot, items, args.jd)
    out = batch.write_outputs(rows)
    show_batch(rows)
    print(f"Results saved to {out}/results.json and results.csv")


if __name__ == "__main__":
    main()
