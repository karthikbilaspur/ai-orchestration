"""Command-line interface for the AI Smart Calculator."""
import sys

import calculator
from llm_client import get_llm
from orchestrator import PlanError, solve


def show(result: dict) -> None:
    print("\nCalculator steps:")
    for s in result["steps"]:
        print(f"  {s['id']}. {s['description']} -> {s['result']:,}")
    print("\nExplanation:")
    print(result["explanation"])
    print(f"\n=> Answer: {result['final']:,}\n")


def ask(question: str, llm) -> None:
    try:
        show(solve(question, llm))
    except (PlanError, calculator.CalculationError) as exc:
        print(f"Sorry, I couldn't solve that: {exc}\n")


def main() -> None:
    llm = get_llm()
    if len(sys.argv) > 1:
        ask(" ".join(sys.argv[1:]), llm)
        return
    print("AI Smart Calculator - type a math problem in English (or 'quit').")
    while True:
        try:
            question = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if question.lower() in {"quit", "exit", "q"}:
            break
        if question:
            ask(question, llm)


if __name__ == "__main__":
    main()
