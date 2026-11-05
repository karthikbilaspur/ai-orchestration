"""Batch mode: screen many resumes (the '200 a day' case) and write results."""
import csv
import json
from collections import Counter
from pathlib import Path
import config


def load_json(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    items = []
    for i, item in enumerate(data, 1):
        if isinstance(item, str):
            items.append({"id": f"R{i:03d}", "resume": item})
        else:
            items.append({"id": item.get("id", f"R{i:03d}"), "resume": item["resume"],
                          "job_description": item.get("job_description")})
    return items


def load_dir(directory):
    return [{"id": p.stem, "resume": p.read_text(encoding="utf-8")}
            for p in sorted(Path(directory).glob("*.txt"))]


def run_batch(orchestrator, items, default_jd):
    rows = []
    for item in items:
        state = orchestrator.screen(item["resume"], item.get("job_description") or default_jd, item["id"])
        row = state.full()
        row["id"] = item["id"]
        rows.append(row)
    return rows


def write_outputs(rows, out_dir=config.OUTPUT_DIR):
    out_dir = Path(out_dir)
    out_dir.mkdir(exist_ok=True)
    (out_dir / "results.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    with open(out_dir / "results.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "name", "status", "score", "reason", "skills"])
        for r in rows:
            writer.writerow([r["id"], r["name"], r["status"],
                             "" if r["score"] is None else r["score"],
                             r["reason"], "; ".join(r["skills"])])
    return out_dir


def summarize(rows):
    return Counter(r["status"] for r in rows)
