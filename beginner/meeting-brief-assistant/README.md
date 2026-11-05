# Personal Meeting Assistant: Parallel + Merge AI Orchestration

You have back-to-back meetings and need a pre-meeting brief in seconds.

```
"I have a meeting with Flipkart team at 2 PM about AI integration"
                         |
                  parse (company, time, topic)
                 /                             \
   Agent A: tech stack (3 points)     Agent B: 5 smart questions     <- run at the same time
                 \                             /
                  Merger Agent -> 1-page cheat-sheet (Intro + Questions)
```

| Agent | Job | Tech |
|---|---|---|
| Agent A: TechStackAgent | 3 points on the company's tech stack | built-in research notes, else LLM "imagine", else labelled assumptions |
| Agent B: QuestionsAgent | 5 questions + why each matters | question bank (+ optional LLM, validated) |
| Merger Agent | Intro + tech snapshot + questions in under 45 lines | template (+ optional LLM intro) |

## Why parallel
A and B do not need each other's output, so they run in two threads. With each agent taking 0.5s, the brief takes about 0.5s instead of 1s (see `log.txt`).
Agents never write to shared state; they return their result and only the orchestrator stores it, so threads cannot clash.

## Built for real life
- If one agent fails or times out, the brief is still produced (tech section says "unavailable", or the question bank is used).
- Every tech section states its source and whether it is researched, AI-generated or an assumption.
- The Flipkart notes come from public web sources (checked 2026-11-03), not official statements. Verify before quoting.
- Back-to-back mode sorts meetings by time and writes one brief per meeting.

## Run
```bash
pip install -r requirements.txt     # optional; core runs on stdlib only
python main.py                      # the task example
python main.py --request "Meeting with Zomato team at 3 PM about cloud migration"
python main.py --file sample_requests.txt     # a whole day
SIMULATED_LATENCY=0 python main.py            # switch off the demo delay
pytest -q
```
Optional LLM mode: `export ANTHROPIC_API_KEY=your_key`.

Add companies in `tools/company_profiles.py`, or replace `lookup()` with a real search API.

## Structure
```
main.py  orchestrator.py  parser.py  writer.py  config.py  state.py  llm.py  logger_setup.py
agents/ (tech_stack_agent, questions_agent, merger_agent)   tools/company_profiles.py
tests/test_assistant.py   sample_requests.txt   log.txt   output/
```
