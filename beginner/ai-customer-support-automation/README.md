# AI Customer Support Automation

A runnable, multi-agent Python project that understands customer complaints,
assigns urgency, proposes resolutions, and escalates cases when needed.

## Agents

1. **Classifier Agent** — categorizes a complaint (billing, technical, account,
   delivery, product, or other).
2. **Priority Agent** — assigns low, medium, high, or critical priority using
   impact, outage language, and customer context.
3. **Resolver Agent** — provides category-specific troubleshooting and next steps.
4. **Escalation Agent** — recommends human handoff when the customer requests it,
   the issue is critical, or automated troubleshooting has failed.

## Features

- Interactive five-question customer intake.
- Conditional workflow and agent handoffs.
- Transparent rule-based classification and priority scoring.
- Human escalation decision with reason.
- JSON case report export.
- Application logging to `log.txt`.
- Unit tests using Python's built-in `unittest`.

This is a self-contained educational implementation. It uses deterministic rules,
not a hosted LLM, and requires no API key or third-party package. The agent
interfaces are separated so an LLM or ticketing platform can be integrated later.

## Requirements

- Python 3.10 or newer
- No external dependencies

## Run the application

```bash
python main.py
```

Answer the five prompts. The system prints a support summary and saves
`support_case_report.json` in the project root.

## Run tests

```bash
python -m unittest discover -s tests -v
```

## Project structure

```text
ai_customer_support_automation/
├── support_system/
│   ├── __init__.py
│   ├── models.py
│   ├── workflow.py
│   └── agents/
│       ├── __init__.py
│       ├── classifier.py
│       ├── priority.py
│       ├── resolver.py
│       └── escalation.py
├── tests/
│   ├── __init__.py
│   ├── test_classifier.py
│   ├── test_priority.py
│   ├── test_resolver.py
│   ├── test_escalation.py
│   └── test_workflow.py
├── main.py
├── requirements.txt
├── log.txt
├── README.md
└── .gitignore
```

## Workflow

```text
Customer Intake
      |
      v
Classifier Agent --> Priority Agent
                         |
                         v
                   Resolver Agent
                         |
                         v
                 Escalation Agent
                    /        \
              Human handoff   Self-service
```

## Safety and production notes

- Never put passwords, payment-card numbers, or authentication codes in a
  customer complaint.
- The rules are illustrative. Validate priority thresholds and response templates
  against your organization's support policy before production use.
- The application does not actually contact a human representative or modify
  customer accounts; it generates a handoff recommendation and case report.
