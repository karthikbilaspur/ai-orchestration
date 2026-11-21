"""Command-line entry point.

    python main.py --demo                       run 5 scripted scenarios, write log.txt
    python main.py --query "laptop under 900 for coding"
    python main.py --interactive                chat-style session (default)
    python main.py --list-catalog               show the sample products
"""
from __future__ import annotations

import argparse
import logging
import sys
from typing import List

from shopping_assistant import ShoppingAssistant
from shopping_assistant.config import DISCLAIMER, money
from shopping_assistant.logging_config import setup_logging

DEMO_QUERIES = [
    ("Plain request with budget, needs and priorities",
     "I need a laptop under 1000 for coding and travel, lightweight with good battery", None),
    ("Headphones with several needs",
     "wireless noise cancelling headphones for the office under $300", None),
    ("Shoes with a priority word",
     "running shoes for a marathon, cushioned, max 200", None),
    ("Vague request - the collector asks follow-up questions (scripted answers)",
     "help me pick something nice", ["backpack", "under $100", "hiking and travel"]),
    ("Budget too low - the research agent stretches it",
     "gaming laptop under 500", None),
]


def scripted_input(answers: List[str]):
    """Return an input() stand-in that replays `answers` (used by the demo)."""
    queue = list(answers)

    def fake_input(prompt: str) -> str:
        answer = queue.pop(0) if queue else ""
        print(f"  [assistant asks] {prompt.strip()}\n  [shopper answers] {answer or '(skipped)'}")
        return answer

    return fake_input


def run_demo(assistant: ShoppingAssistant) -> None:
    for i, (title, query, answers) in enumerate(DEMO_QUERIES, start=1):
        print("=" * 78)
        print(f"Scenario {i}: {title}")
        print("=" * 78)
        result = assistant.run(query, input_fn=scripted_input(answers) if answers else None)
        print(assistant.report(result))
        print()


def run_interactive(assistant: ShoppingAssistant) -> None:
    print("AI Shopping Assistant - describe what you want, or type 'quit'.")
    print(DISCLAIMER)
    while True:
        try:
            query = input("\nWhat are you looking for? > ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if query.lower() in {"q", "quit", "exit"}:
            break
        if not query:
            continue
        result = assistant.run(query, input_fn=input)
        print()
        print(assistant.report(result))


def list_catalog(assistant: ShoppingAssistant) -> None:
    for category in assistant.catalog.categories():
        print(f"\n{category.replace('_', ' ').upper()}")
        for p in assistant.catalog.by_category(category):
            print(f"  {p.id:8} {p.name:26} {money(p.price):>7}  {p.rating:.1f}/5  tags: {', '.join(p.tags)}")


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="AI E-commerce Shopping Assistant (demo, never buys anything)")
    parser.add_argument("--demo", action="store_true", help="run the scripted demo scenarios")
    parser.add_argument("--query", help="run a single request and print the report")
    parser.add_argument("--interactive", action="store_true", help="start an interactive session")
    parser.add_argument("--list-catalog", action="store_true", help="print the sample catalog")
    parser.add_argument("--log-file", default="log.txt", help="where to write the run log (default: log.txt)")
    parser.add_argument("--verbose", action="store_true", help="also print log lines to the console")
    args = parser.parse_args(argv)

    setup_logging(args.log_file, level=logging.INFO, console=args.verbose)
    assistant = ShoppingAssistant()

    if args.list_catalog:
        list_catalog(assistant)
    elif args.demo:
        run_demo(assistant)
        print(f"(full step-by-step log written to {args.log_file})")
    elif args.query:
        print(assistant.report(assistant.run(args.query)))
    else:
        run_interactive(assistant)
    return 0


if __name__ == "__main__":
    sys.exit(main())
