
import argparse, json, sys
from .orchestrator import BugTriageOrchestrator

def print_result(r):
    print(f"\n🔍 CLASSIFICATION: {r.classification.category.upper()} (conf {r.classification.confidence})")
    print(f"   {r.classification.reasoning}")
    print(f"   Route → {r.route} | File: {r.parsed.file}:{r.parsed.line} | Exception: {r.parsed.exception_type}")
    print(f"\n🛠️  FIX: {r.fix.title}\n   Root cause: {r.fix.root_cause}\n\n{r.fix.diff}\n\n   {r.fix.explanation}")
    print(f"\n✅ VERIFY:"); [print(f"   - {v}") for v in r.fix.verification]
    print(f"\n🧑‍⚖️ REVIEWER: {r.review.verdict} — {r.review.feedback} (iterations: {r.iterations})")

if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("error", nargs="?", help="Error message"); ap.add_argument("--file", help="File with error"); ap.add_argument("--json", action="store_true"); ap.add_argument("--demo", action="store_true")
    a=ap.parse_args()
    if a.demo:
        raw="ModuleNotFoundError: No module named 'pandas'"
    elif a.file:
        raw=open(a.file).read()
    elif a.error: raw=a.error
    else: raw=sys.stdin.read()
    r=BugTriageOrchestrator().triage(raw)
    print(r.model_dump_json(indent=2) if a.json else print_result(r))
