"""Batch mode: process many submissions, write an audit trail for Finance."""
import csv
import datetime
import json
from collections import Counter
from pathlib import Path

import config
from state import APPROVED, MANAGER


def load(path):
    p = Path(path)
    if p.suffix.lower() == ".json":
        data = json.loads(p.read_text(encoding="utf-8"))
        items = []
        for i, it in enumerate(data, 1):
            if isinstance(it, str):
                it = {"message": it}
            items.append({"id": it.get("id", f"E{i:03d}"), "message": it["message"],
                          "sender": it.get("sender"), "attachments": it.get("attachments", [])})
        return items
    return [{"id": f"E{i:03d}", "message": line, "sender": None, "attachments": []}
            for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1) if line.strip()]


def run_batch(bot, items):
    rows = []
    for it in items:
        s = bot.process(it["message"], it["sender"], it["attachments"], it["id"])
        row = s.full()
        row["id"] = it["id"]
        rows.append(row)
    return rows


def write_outputs(rows, out_dir=config.OUTPUT_DIR):
    out_dir = Path(out_dir)
    out_dir.mkdir(exist_ok=True)
    (out_dir / "results.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
    stamp = datetime.datetime.now().isoformat(timespec="seconds")
    with open(out_dir / "decisions.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["timestamp", "id", "sender", "amount", "currency", "category", "place", "bill",
                    "decision", "rule", "message"])
        for r in rows:
            w.writerow([stamp, r["id"], r["sender"] or "", "" if r["amount"] is None else f'{r["amount"]:g}',
                        r["currency"], r["category"], r["place"] or "", r["bill"],
                        r["decision"], r["rule"], r["message"]])
    return out_dir


def summarize(rows):
    counts = Counter(r["decision"] for r in rows)
    approved = sum(r["amount"] or 0 for r in rows if r["decision"] == APPROVED)
    pending = sum(r["amount"] or 0 for r in rows if r["decision"] == MANAGER and r["currency"] == "INR")
    return counts, approved, pending
