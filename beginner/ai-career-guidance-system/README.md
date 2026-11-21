# AI Career Guidance System

A practical, multi-agent Python project that interviews a learner, analyzes skills,
recommends career paths, and creates a personalized 30-day learning roadmap.

## Features

- **Interviewer Agent** collects and validates six learner inputs.
- **Skill Analyzer Agent** identifies strengths, transferable skills, and gaps.
- **Career Recommendation Agent** scores AI/ML, software development, data science,
  and cybersecurity against interests, background, and known languages.
- **Learning Roadmap Agent** creates a 30-day plan based on available daily study time
  and preference for theory or hands-on work.
- **Agent handoffs** are orchestrated in a clear sequential workflow.
- JSON report export and application logging.

This project uses only the Python standard library; no API key or paid AI service is
required. The agents use transparent rule-based logic, making the project easy to
understand, test, and extend with an LLM later.

## Requirements

- Python 3.10+
- No third-party packages required

## Run

From this directory:

```bash
python main.py
```

To run the automated tests:

```bash
python -m unittest discover -s tests -v
```

The interactive run prints a report and saves it to `career_report.json`.
Application activity is appended to `log.txt`.

## Example inputs

- Education: B.Tech in Computer Science
- Languages: Python, JavaScript
- Interests: AI, data science
- Daily learning time: 2 hours
- Learning preference: hands-on projects
- Target: internship

## Project structure

```text
ai_career_guidance_system/
├── career_guidance/
│   ├── __init__.py
│   ├── models.py
│   ├── workflow.py
│   └── agents/
│       ├── __init__.py
│       ├── interviewer.py
│       ├── skill_analyzer.py
│       ├── career_recommender.py
│       └── roadmap.py
├── tests/
│   ├── test_interviewer.py
│   ├── test_skill_analyzer.py
│   ├── test_recommender.py
│   ├── test_roadmap.py
│   └── test_workflow.py
├── main.py
├── requirements.txt
├── README.md
├── log.txt
└── .gitignore
```

## How the workflow works

1. The interviewer gathers a `LearnerProfile`.
2. The skill analyzer converts the profile into strengths and skill gaps.
3. The recommender ranks career tracks and explains each match.
4. The roadmap agent creates a 30-day schedule for the top recommendation.
5. The workflow combines all outputs into a report and writes JSON.

## Extending the project

You can replace each agent's rule-based logic with an LLM/API call while retaining
the same input/output contracts. Add a web interface (Streamlit/FastAPI), a database,
or a job-description matching agent as future enhancements.

## Disclaimer

Recommendations are educational guidance, not a guarantee of employment. A learner
should validate choices through projects, mentorship, and current job-market research.
