# Project 12 — AI Research Assistant with Fact Checker
**Time:** 2–3 hours | **Pattern:** Sequential + Verification | **Routing:** Confidence-based

> A user asks a question and wants a reliable, structured answer.
> This project implements: Planner → Researcher → Fact Checker → Confidence Check → Report / Research Again

## Architecture
```
User Question
     |
Research Planner (breaks question into subtopics)
     |
Research Agent (gathers from predefined documents / sources)
     |
Fact Checker Agent (checks claims against retrieved evidence)
     |
  Confidence Check
   /          \
Pass          Fail
 |              |
Report       Research Again (retry loop, max 2 retries)
```

## What You'll Learn
- Agent verification
- Retry loops
- Confidence-based routing
- Evidence-grounded reporting with citations

## Quick Start
```bash
pip install -r requirements.txt
python main.py --question "What are the benefits and risks of intermittent fasting?"
# or interactive
python main.py
# or web UI
python app.py
# open http://localhost:5000
```

## Demo Questions
- What are the benefits and risks of intermittent fasting?
- How does photosynthesis work?
- What caused the 2008 financial crisis?
- Is coffee good for health?

## Project Structure
```
main.py                 CLI entry
app.py                  Flask web UI
src/
  core/
    orchestrator.py     Sequential + verification orchestration
    models.py           Dataclasses: Claim, Evidence, Report
    config.py           Thresholds, retry limits
  agents/
    planner.py          Research Planner
    researcher.py       Researcher Agent
    fact_checker.py     Fact Checker Agent
    report_agent.py     Report Agent
data/documents/         Predefined knowledge base (markdown)
examples/               Sample outputs
tests/                  Unit tests
```

## How Verification Works
1. Researcher returns claims, each with a source snippet.
2. Fact Checker scores each claim: SUPPORTED / PARTIALLY SUPPORTED / UNSUPPORTED / CONTRADICTED
3. Confidence = weighted % of supported claims + evidence coverage
4. If confidence >= 0.75 → Pass → Report
   If confidence < 0.75 and retries left → Research Again with refined queries
   Else → Report with low-confidence warning + unverified claims section

## Customizing Sources
Add `.md` files to `data/documents/`. Each file becomes a source. Format:
```markdown
# Title
Content...
```
The Researcher does keyword + semantic-ish (TF-IDF via sklearn if available, else keyword) retrieval.

## Configuration
Edit `src/core/config.py`:
- CONFIDENCE_THRESHOLD = 0.75
- MAX_RETRIES = 2
- MAX_SUBTOPICS = 4
- MAX_CLAIMS_PER_SUBTOPIC = 5
