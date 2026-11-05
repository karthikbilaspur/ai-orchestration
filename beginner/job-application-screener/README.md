# Job Application Screener: Conditional AI Orchestration

HR receives 200 resumes a day. Three small agents screen each one automatically, and the pipeline **stops early** when a candidate fails a hard requirement.

```
resume + job description
        |
 [Extractor Agent]  -> list the skills (ignores denied ones like "No AI experience")
        |
 [Checker Agent]    -> Python missing?  YES -> Rejected, STOP (Scorer never runs)
        |                AI/LLM missing? YES -> Weak Match, continue
        v
 [Scorer Agent]     -> score 1-10 + 2-line reason -> final status
```

| Agent | Job | Tech |
|---|---|---|
| Extractor | skills + candidate name, negation-aware | rules (+ optional LLM, validated against the resume text) |
| Checker | hard reject / weak match / strong match | plain Python rules only |
| Scorer | rule-based score, 2-line reason | rules (+ optional LLM rewording of the reason) |

## Final statuses
- `Rejected` : no Python (stop), or Weak Match with score below 5, or low score
- `Weak Match` : no AI/LLM but a solid profile (score 5, the cap), sent to a human
- `Review` : meets requirements, thin evidence (score 5-6)
- `Shortlisted` : strong match, score 7+

Task output example:
```json
{"status": "Rejected", "reason": "No AI/LLM skills"}
```

## Run
```bash
pip install -r requirements.txt        # optional; core runs on stdlib only
python main.py                         # task example + 7 sample resumes
python main.py --resume "Name: Ali. Skills: Python, LangChain" --jd "Need Python + AI/LLM intern"
python main.py --batch sample_resumes.json
python main.py --resume-dir my_resumes/    # folder of .txt files
pytest -q
```
Optional LLM mode: `export ANTHROPIC_API_KEY=your_key`.

Every step is logged to `log.txt`; batch results go to `output/results.json` and `output/results.csv`.

## Structure
```
main.py  orchestrator.py  batch.py  config.py  state.py  skills_taxonomy.py  llm.py  logger_setup.py
agents/ (extractor_agent, checker_agent, scorer_agent)   tests/test_screener.py
sample_resumes.json   log.txt   output/
```
