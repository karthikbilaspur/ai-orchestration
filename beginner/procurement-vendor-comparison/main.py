"""CLI entry point."""
import argparse, json, pathlib
from models import Vendor
from orchestrator import Orchestrator
from utils import load_json, render_report, log
def main():
    p = argparse.ArgumentParser(description="AI Procurement & Vendor Comparison Assistant")
    p.add_argument("--requirements", default="Need 50 laptops, budget 4000000 INR, 16GB RAM, 512GB SSD, delivery within 14 days, 3 year warranty")
    p.add_argument("--requirements-file")
    p.add_argument("--vendors", default="data/vendors.json")
    p.add_argument("--weights", default="data/weights.json")
    p.add_argument("--output", default="output/comparison_report.md")
    p.add_argument("--demo", action="store_true")
    a = p.parse_args()
    req_text = pathlib.Path(a.requirements_file).read_text().strip() if a.requirements_file else a.requirements
    vendors = [Vendor(**v) for v in load_json(a.vendors)]
    weights = load_json(a.weights)
    req, scores, winner, rationale = Orchestrator(weights).run(req_text, vendors)
    report = render_report(req, scores, winner, rationale)
    pathlib.Path(a.output).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(a.output).write_text(report)
    print("\n"+report); print(f"\nSaved to {a.output}")
if __name__ == "__main__": main()
