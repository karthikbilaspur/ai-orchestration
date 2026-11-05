"""Entry point.

Usage:
  python main.py                      # run the main example + all samples
  python main.py -m "your message"    # handle one custom message
  python main.py --samples            # run only sample_messages.json
"""
import argparse
import json
from pathlib import Path

from orchestrator import SupportOrchestrator

MAIN_EXAMPLE = ("Where is my order? I ordered shoes 3 days ago, "
                "Order ID SHOE998, still not delivered!")


def show(state) -> None:
    print("\n" + "=" * 70)
    print("CUSTOMER :", state.message)
    print("INTENT   :", state.intent, "| sentiment:", state.sentiment)
    print("ORDER ID :", state.order_id, "| tracking:", (state.tracking or {}).get("status"))
    print("ESCALATE :", state.escalate)
    print("REPLY    :", state.reply)


def main() -> None:
    parser = argparse.ArgumentParser(description="E-commerce support orchestrator")
    parser.add_argument("-m", "--message", help="handle a single message")
    parser.add_argument("--samples", action="store_true", help="run only the sample file")
    args = parser.parse_args()

    bot = SupportOrchestrator()
    if args.message:
        show(bot.handle(args.message))
        return

    messages = [] if args.samples else [MAIN_EXAMPLE]
    samples = json.loads((Path(__file__).parent / "sample_messages.json").read_text())
    messages += [m for m in samples if m != MAIN_EXAMPLE or args.samples]
    for msg in messages:
        show(bot.handle(msg))


if __name__ == "__main__":
    main()
