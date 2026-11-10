# Project 15 — AI Customer Feedback Intelligence

## Architecture
```
        100 Reviews
              |
        Review Splitter
        /    |    |    \
  Sentiment Product Service Trends
        \    |    |    /
         Merger Agent
              |
        Insight Report
```

## How it works
1. **Review Splitter** (`main.py`): loads reviews, fans them out to 4 agents in parallel.
2. **Parallel Agents** (`agents/`): each independent, stateless, runs concurrently via `ThreadPoolExecutor`.
   - `sentiment_agent.py` — positive / negative / neutral
   - `product_agent.py` — product issues (quality, durability, packaging, features)
   - `service_agent.py` — service complaints (delivery, support, refund, staff)
   - `trend_agent.py` — recurring patterns / frequent keywords
3. **Merger Agent** (`agents/merger_agent.py`): aggregates counts, ranks issues by frequency, produces prioritized recommendations.
4. **Insight Report**: console + `insight_report.md` + trace in `log.txt`.

## What you'll learn
Parallel execution, aggregation / fan-in, batch processing.

## Run
```bash
python main.py
python main.py --reviews reviews.json --output insight_report.md
python -m pytest tests/ -v
```

## Input
List of `{"id": 1, "text": "...", "rating": 4}`. If no file given, generates 100 sample reviews.
