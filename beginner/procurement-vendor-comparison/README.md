# Project 20 — AI Procurement & Vendor Comparison Assistant
**Time:** 2–3 hours | **Theme:** Decision-making orchestration | **Stack:** Python 3.9+, no external deps

A company wants to compare three vendors before purchasing a product or service.

## Orchestration
```
User Requirements
       |
Requirement Agent
       |
   +---+---+---+
   |   |   |   |
Vendor Price Risk Analysis (parallel)
   |   |   |
   +---+---+
       |
 Decision Agent
       |
 Comparison Report
```

## Agents
1. **Requirement Agent** — extracts budget, specifications and requirements.
2. **Vendor Analysis Agent** — evaluates vendor info from mock JSON data.
3. **Pricing Agent** — compares costs.
4. **Risk Agent** — checks delivery, warranty and reliability factors.
5. **Decision Agent** — creates a recommendation.

## What you'll learn
Parallel analysis, weighted scoring, decision orchestration.

## Quick Start
```bash
pip install -r requirements.txt
python main.py
# or with your own requirements:
python main.py --requirements "Need 50 laptops, budget 4000000 INR, 16GB RAM, 512GB SSD, delivery within 14 days, 3 year warranty"
python main.py --vendors data/vendors.json --requirements-file data/sample_requirements.txt --weights data/weights.json --output output/comparison_report.md
python main.py --demo
```

## Files
| File | What it does |
|---|---|
| `main.py` | CLI + orchestration entry point |
| `agents.py` | All 5 agents |
| `orchestrator.py` | Parallel orchestration + weighted scoring |
| `models.py` | Dataclasses: Requirement, Vendor, Scores |
| `utils.py` | Logging, JSON loading, report rendering |
| `data/vendors.json` | Mock vendor data (3 vendors) |
| `data/sample_requirements.txt` | Example user request |
| `data/weights.json` | Default weights (must sum to 1.0) |
| `tests/test_*.py` | Unit tests (unittest, no pytest needed) |
| `run_tests.py` | Test runner |
| `log.txt` | Sample run log |
| `output/comparison_report.md` | Generated report (from demo run) |

## Weighted Scoring
Default: Price 35%, Spec Fit 30%, Risk 20%, Delivery 15%.
Score = 0-100 per vendor. Higher wins. Tie-break: lower total cost, then lower risk.

## Example Output
```
Vendor A — TechNova: 82.4 (Price 78, Spec 90, Risk 85, Delivery 80)
Vendor B — PrimeSupply: 76.1
Vendor C — ValueKart: 68.9
RECOMMENDATION: TechNova
```
