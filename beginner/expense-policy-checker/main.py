"""Entry point.

Usage:
  python main.py                                   # the task example
  python main.py -m "Spent Rs 700 on lunch at Toit, no bill" [--sender Ravi] [--attach bill.jpg]
  python main.py --file sample_expenses.json       # a batch (also accepts a .txt, one message per line)
"""
import argparse
import json

import batch
from orchestrator import ExpenseOrchestrator

MAIN_MESSAGE = "Hi, spent Rs. 1200 on client dinner at Toit, Bangalore. No bill attached."


def show_single(s) -> None:
    print("\n" + "=" * 70)
    print("OUTPUT :", json.dumps(s.result()))
    place = f"{s.place} ({s.city})" if s.city else s.place
    print("Parsed :", f"Amount={s.parsed()['Amount']} | Category={s.category} | Bill={s.bill} | Place={place}"
                      f" | client={s.client_related}")
    print("Rule   :", f"{s.rule_id} ({s.rule_description})")
    print("Reply  :", s.reply)


def main() -> None:
    parser = argparse.ArgumentParser(description="Expense & policy checker")
    parser.add_argument("-m", "--message", help="one expense message")
    parser.add_argument("--sender", help="who sent it")
    parser.add_argument("--attach", action="append", default=[], help="attached file name (repeatable)")
    parser.add_argument("--file", help="JSON or text file with many submissions")
    args = parser.parse_args()

    bot = ExpenseOrchestrator()
    if args.file:
        rows = batch.run_batch(bot, batch.load(args.file))
        out = batch.write_outputs(rows)
        print("\n" + "=" * 78)
        print(f"{'ID':<6}{'Sender':<8}{'Rs':<7}{'Bill':<9}{'Decision':<16}{'Rule':<16}")
        for r in rows:
            amt = "-" if r["amount"] is None else f"{r['amount']:g}"
            print(f"{r['id']:<6}{(r['sender'] or '-'):<8}{amt:<7}{r['bill']:<9}{r['decision']:<16}{r['rule']:<16}")
        counts, approved, pending = batch.summarize(rows)
        print("\nSummary:", dict(counts))
        print(f"Auto-approved total: Rs {approved:g} | waiting for managers: Rs {pending:g}")
        print(f"Audit trail saved to {out}/decisions.csv")
        return

    show_single(bot.process(args.message or MAIN_MESSAGE, args.sender, args.attach))


if __name__ == "__main__":
    main()
