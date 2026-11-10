"""CLI entry point."""
import argparse, sys
from pathlib import Path
from db_setup import setup
from config import DB_PATH
from orchestrator import run

def main():
    ap = argparse.ArgumentParser(description="Project 18 - AI SQL Query Assistant")
    ap.add_argument("--question", "-q", help="Question in plain English")
    ap.add_argument("--interactive", "-i", action="store_true")
    args = ap.parse_args()
    if not DB_PATH.exists():
        print("Seeding database..."); setup()
    def ask(q):
        out = run(q)
        print("\n--- SQL ---\n", out.get("sql"))
        print("\n--- Explanation ---\n", out.get("explanation"))
        if out.get("error"): print("ERROR:", out["error"])
    if args.question:
        ask(args.question)
    elif args.interactive:
        print("AI SQL Assistant (type 'exit' to quit)")
        while True:
            q = input("\nAsk: ").strip()
            if q.lower() in ("exit","quit"): break
            if q: ask(q)
    else:
        ap.print_help()

if __name__ == "__main__":
    main()
