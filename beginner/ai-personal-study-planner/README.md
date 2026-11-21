# AI Personal Study Planner

A multi-agent study planner written in pure Python (standard library only). Give it a subject, your
level, a deadline and how many hours a day you can study; it returns a subject-aware topic outline,
a priority-weighted day-by-day schedule that ends exactly on your deadline, practice questions, and a
progress tracker you can update from the command line.

> It uses transparent templates and heuristics rather than a hosted LLM, so it runs offline, is fully
> deterministic, and is easy to test. It does not replace a teacher's syllabus or official exam requirements.

## Features

- **Six validated inputs** with friendly re-prompting, plus non-interactive modes (`--from-json`, CLI flags).
- **Subject-aware topics**: programming, maths, science, language or generic outlines, adjusted for
  beginner / intermediate / advanced learners.
- **Priority weighting**: your difficult topics become *high* priority and are studied more often (3:2:1
  weighting using a smooth round-robin, so they are spread out rather than bunched together).
- **Deadline-aware schedule**: one session per day from the start date to the deadline, a rotating
  learn -> practice -> self-test cycle per topic, and final revision days for plans of 7+ days.
- **Assessment preference**: *daily quizzes* (a question per study session) or *weekly assessments*
  (a timed assessment every 7th day covering that week's topics).
- **Progress tracking**: mark sessions done/undone; see percent complete, hours, per-topic stats,
  overdue sessions, streak and a status (`not started`, `on track`, `slightly behind`, `behind schedule`, `complete`).
- **Persistent & safe**: atomic JSON writes, clear errors for corrupt or missing files.
- **Logging**: every agent handoff and error is written to `log.txt`.

## Agents

| Agent | File | Responsibility |
|-------|------|----------------|
| Requirement Collector | `agents/collector.py` | Asks/validates the six inputs (interactive, dict or JSON) |
| Topic Breakdown | `agents/topic_breakdown.py` | Builds the outline and assigns priorities |
| Schedule Generator | `agents/schedule.py` | Allocates study, assessment and revision sessions per day |
| Quiz Generator | `agents/quiz.py` | Creates practice questions for the chosen assessment style |
| Progress Evaluator | `agents/progress.py` | Computes progress metrics and persists completion |

```
Collector -> Topic Breakdown -> Schedule Generator -> Quiz Generator -> Progress Evaluator
                                         |                                      |
                                  study_plan.json                         progress.json
```

## Requirements

- Python 3.10 or newer
- No third-party packages (see `requirements.txt`)

## Usage

Interactive (answers six questions):

```bash
python main.py
```

Non-interactive, with flags:

```bash
python main.py plan --subject "Python" --level beginner --deadline 2026-12-05 \
    --hours 2 --difficult "Recursion, Error handling" --assessment "weekly assessments"
```

From a JSON file (see `sample_input.json`):

```bash
python main.py plan --from-json sample_input.json
```

Track your progress:

```bash
python main.py show                 # overdue + next 7 days (use --days N to change)
python main.py done 0 1 2           # mark sessions 0, 1, 2 as completed
python main.py undo 2               # un-mark session 2
python main.py status               # progress summary
python main.py --data-dir ~/study plan --from-json sample_input.json   # keep files elsewhere
```

`python -m study_planner ...` works the same way as `python main.py ...`. The exit code is `0` on
success and `1` for validation or file errors.

### Requirements JSON

| Field | Required | Notes |
|-------|----------|-------|
| `subject` | yes | up to 100 characters |
| `level` | yes | `beginner`, `intermediate`, `advanced` |
| `deadline` | yes | `YYYY-MM-DD`, on/after the start date, at most 366 days of study |
| `hours_daily` (or `hours`) | yes | 0.25 - 16 |
| `difficult_topics` | no | list or comma-separated string |
| `assessment` | no | `daily quizzes` (default) or `weekly assessments` |
| `start_date` | no | defaults to today |

## Output files

- `study_plan.json` - requirements, summary, topic priorities, daily schedule, practice questions, progress.
- `progress.json` - completed session numbers and metrics. A new plan resets it.
- `log.txt` - timestamped log of handoffs, saves and errors.

## Project structure

```
ai_personal_study_planner/
├── main.py                  # entry point
├── sample_input.json        # example requirements
├── requirements.txt
├── log.txt
├── study_planner/
│   ├── cli.py               # argparse commands and output formatting
│   ├── models.py            # StudyRequirements + validators
│   ├── workflow.py          # wires agents, persists plan/progress
│   ├── storage.py           # atomic JSON read/write
│   ├── logging_setup.py
│   └── agents/              # collector, topic_breakdown, schedule, quiz, progress
└── tests/                   # unittest suite (56 tests)
```

## Testing

```bash
python -m unittest discover -s tests -v
```

The tests use a fixed date and temporary folders, so they are deterministic and never touch your real
plan files. Optional coverage: `pip install coverage && coverage run -m unittest discover -s tests && coverage report`.

## Design notes

- **Dates are injected** (`today`, `start_date`) so scheduling and progress logic is fully testable.
- **Dicts for sessions/topics** keep the JSON plan human-readable and trivially serialisable.
- **Smooth weighted round-robin** gives deterministic, evenly spread allocation without randomness.

## Limitations

- Topic outlines come from built-in templates, not from your actual syllabus.
- One session per calendar day; there are no rest days or per-weekday hours.
- Progress is tracked per session, not per minute studied.

## Changelog

- **2.0.0** - Added CLI (`plan/show/done/undo/status`), JSON input, priority-weighted scheduling,
  revision and weekly-assessment sessions, quiz agent, richer progress metrics, atomic storage,
  proper logging and a 56-test suite. Fixed: subject validated first, no infinite loop on bad hours input,
  no unbounded schedule for far-future deadlines.
- **1.0.0** - Initial four-agent demo.
