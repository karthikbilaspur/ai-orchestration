# Project 13 — AI Bug Triage & Debugging Assistant
**Time:** 2–3 hours | **Pattern:** Conditional Routing + Validation

Paste an error → classify it → route to the right specialist → propose a fix → validate it.

```
Error Message
     |
Error Classifier
     |
Conditional Router
  /    |     \
Syntax Runtime Dependency  (+ Logic)
  \    |     /
   Solution Agent
        |
    Reviewer Agent
        |
    Final Fix
```

## Quick Start
```bash
pip install -r requirements.txt
python -m src.main --demo
# or
python app.py
# open http://localhost:5000
```

## CLI
```bash
python -m src.main "TypeError: Cannot read properties of undefined (reading 'map')"
python -m src.main --file examples/python_traceback.txt
python -m src.main --json "ModuleNotFoundError: No module named 'pandas'"
```

## How it works
1. **Log Analyzer** — extracts exception type, message, file/line, stack frames, code snippet, env hints.
2. **Error Classifier** — scores Syntax / Runtime / Dependency / Logic / Config / Network.
3. **Conditional Router** — routes ONLY to the relevant specialist prompt / playbook. No generic answer.
4. **Solution Agent** — proposes minimal fix + diff + verification steps, tailored to the route.
5. **Reviewer Agent** — checks: does fix address root cause? Is it minimal? Safe? Testable? Returns APPROVED / NEEDS_REVISION with feedback. Loops max 2x.

## What you'll learn
- Multi-agent routing, specialized agents, validation / self-correction loop
- Structured outputs (Pydantic) between agents
- Deterministic routing + LLM reasoning hybrid (rules first, LLM fallback)
