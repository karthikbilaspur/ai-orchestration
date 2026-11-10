# Project 17 — AI Incident Management System
**Time:** 2–3 hours | **Pattern:** Event-driven routing

A system receives an incident alert and automatically prepares an incident response.

## Architecture
```
System Alert
     |
Alert Analyzer
     |
Severity Classifier
   /      |       \
 Low    Medium   Critical
  |       |         |
 Log    Investigate Escalate
          \         /
         Response
             |
        Notification
```

## Agents
| # | Agent | File | Job |
|---|-------|------|-----|
| 1 | Alert Analyzer | `agents/alert_analyzer.py` | Parse raw alert → service, error_type, metadata |
| 2 | Severity Agent | `agents/severity_agent.py` | low / medium / critical + route (Log / Investigate / Escalate) |
| 3 | Root Cause Agent | `agents/root_cause_agent.py` | Suggest possible causes per error type |
| 4 | Response Agent | `agents/response_agent.py` | Recommend actions by severity + playbook |
| 5 | Notification Agent | `agents/notification_agent.py` | Prepare formatted incident notification |

## What you'll learn
- Event-driven orchestration (each step emits an event)
- Priority routing (severity → route)
- Escalation (critical → page on-call, freeze deploys)

## Setup
```bash
pip install -r requirements.txt  # stdlib only, no deps needed
```

## Run
```bash
# Demo with 4 sample alerts (low → critical)
python main.py

# Single alert
python main.py "ERROR: payment-service timeout - 35% error rate, latency 6200ms"
python orchestrator.py "CRITICAL: database disk full - writes failing"
```

## Tests (4 files, 12 tests)
```bash
python -m pytest tests/ -v
# or without pytest:
python -m unittest discover -s tests -v
```

## Logs
- `logs/incidents.log` — human-readable notifications (appended on every alert)
- `logs/events.jsonl` — one JSON event per pipeline step (`alert_received`, `severity_classified`, `routed_to_*`, `response_prepared`, `notification_prepared`)

## Example output
```
🔴 [CRITICAL] INC-... - payment-service | TimeoutError
Route: Escalate
Possible causes: Downstream service slow...
Recommended actions: PAGE on-call immediately...
```

## Extend ideas
- Plug in an LLM for Analyzer / Root Cause instead of rules
- Add Slack / PagerDuty sender in Notification Agent
- Add deduplication + incident grouping
