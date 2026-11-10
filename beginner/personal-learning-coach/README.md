# Project 16 — AI Personal Learning Coach
Adaptive orchestration • 2-3 hours

## Problem
A learner enters a topic and receives a personalized study plan and quiz.

## Agents
1. **Skill Assessment Agent** – evaluates current level
2. **Planner Agent** – creates learning roadmap
3. **Tutor Agent** – explains topic
4. **Quiz Agent** – generates questions
5. **Evaluator Agent** – evaluates answers, recommends next topic

## Orchestration / Flow
```
User Topic → Skill Assessment → Learning Planner → Tutor → Quiz → Evaluation
                                                              ↓
                                                        Weak Topic?
                                                       /         \
                                                    Yes           No
                                                     |             |
                                                  Revise      Next Topic
```

## What You'll Learn
Feedback loops, adaptive workflows, state management.

## Tech Stack
Python • Gemini API • Streamlit • Pydantic • concurrent.futures • JSON/SQLite • Python logging

## Quick Start
```bash
pip install -r requirements.txt
cp .env.example .env   # add GEMINI_API_KEY
streamlit run app.py
```
Without a key, the app runs in MOCK mode with fallback content so you can test the loop.

## Project Structure
```
app.py            # Streamlit UI + SQLite persistence
agents.py         # 5 agents
orchestrator.py   # Feedback loop / routing
state.py          # Pydantic LearnerState
tests/            # pytest tests
logs/             # app.log, test.log
requirements.txt
README.md
```

## Tests
```bash
pytest tests/ -v
```

## How Adaptation Works
- Score < 0.7 → `revise` → same step, Tutor focuses on weak topics, Quiz gets easier
- Score >= 0.7 → `next_topic` → current_step += 1
- All progress saved in `learning.db` (SQLite) and resumable from sidebar.
