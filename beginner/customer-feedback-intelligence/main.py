"""Orchestrator - fan-out to 4 agents in parallel, fan-in via Merger Agent."""
import argparse, json, random, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from agents import sentiment_agent, product_agent, service_agent, trend_agent
from agents.merger_agent import run as merge

SAMPLES = [
    ("I love this product, excellent quality and fast delivery", 5),
    ("Terrible quality, broken on arrival and support was rude", 1),
    ("Delivery was late and refund process is slow", 2),
    ("Great value, beautiful packaging, easy to use", 5),
    ("Battery is defective and size is wrong", 2),
    ("Support was helpful but shipping took too long", 3),
    ("Amazing product, I will recommend it to everyone", 5),
    ("Poor material, color faded after one wash", 2),
    ("Good product but delivery delay ruined the experience", 3),
    ("Cancelled order, no refund yet, very frustrated", 1),
]

def load_reviews(path):
    if path and Path(path).exists():
        return json.loads(Path(path).read_text())
    random.seed(42)
    return [{"id": i + 1, "text": t, "rating": r} for i in range(100) for t, r in [random.choice(SAMPLES)]]

def log(msg):
    print(msg)
    with open("log.txt", "a", encoding="utf-8") as f:
        f.write(msg + "\n")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reviews", default=None)
    ap.add_argument("--output", default="insight_report.md")
    args = ap.parse_args()
    Path("log.txt").write_text(f"=== Run started {time.strftime('%Y-%m-%d %H:%M:%S')} ===\n")
    reviews = load_reviews(args.reviews)
    log(f"[Splitter] Split {len(reviews)} reviews -> 4 agents")
    with ThreadPoolExecutor(max_workers=4) as ex:
        f = {
            "sentiment": ex.submit(sentiment_agent.run, reviews),
            "product": ex.submit(product_agent.run, reviews),
            "service": ex.submit(service_agent.run, reviews),
            "trend": ex.submit(trend_agent.run, reviews),
        }
        results = {}
        for name, fut in f.items():
            results[name] = fut.result()
            log(f"[{name.capitalize()} Agent] Done -> {str(results[name])[:220]}")
    report = merge(results["sentiment"], results["product"], results["service"], results["trend"], len(reviews))
    Path(args.output).write_text(report, encoding="utf-8")
    log(f"[Merger Agent] Combined 4 outputs -> {args.output}")
    log("=== Run finished ===")
    print("\n" + report)

if __name__ == "__main__":
    main()
