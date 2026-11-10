"""CLI entry for Project 12."""
import argparse, json, sys
from src.core.orchestrator import run_research

def main():
    p = argparse.ArgumentParser(description="AI Research Assistant with Fact Checker")
    p.add_argument("--question", type=str, help="Research question")
    p.add_argument("--json", action="store_true", help="Output JSON")
    p.add_argument("--threshold", type=float, default=0.75)
    p.add_argument("--retries", type=int, default=2)
    args = p.parse_args()
    q = args.question or input("🔍 Enter your research question: ").strip()
    if not q:
        print("Please provide a question."); sys.exit(1)
    result = run_research(q, confidence_threshold=args.threshold, max_retries=args.retries)
    if args.json:
        print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
    else:
        print(result.to_markdown())
        print(f"\n✅ Confidence: {result.confidence:.0%} | Status: {result.status} | Retries used: {result.retries_used}")

if __name__ == "__main__":
    main()
