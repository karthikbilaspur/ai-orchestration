# AI Meeting Assistant

A multi-agent meeting assistant written in pure Python (standard library only). Give it a meeting
transcript and it produces a summary, decisions, action items (with owners, deadlines and priority),
Markdown minutes and an optional follow-up email draft.

> It uses transparent heuristics rather than a hosted LLM, so it runs offline, is deterministic and is
> easy to test. Extraction is heuristic: always review the output before sending it to anyone.

## Features

- **Flexible transcripts**: `[00:01:23] Maya: ...` timestamps, `Name:` speaker labels, plain text, and
  `Decision:` / `Action:` / `TODO:` labelled lines. Abbreviations like "Dr." do not break sentences.
- **Extractive summary**: ranks sentences by topic relevance and decision/action cues; *short* (<= 3
  sentences, one paragraph) or *detailed* (<= 8 bullets with speakers). Also lists key topics.
- **Decisions**: detects "decided / agreed / approved / going with ..." and ignores questions,
  conditionals ("if we decide...") and negations ("we haven't decided yet").
- **Action items**: commitments ("Sam will ..."), first-person ("I'll ..." -> the speaker), requests
  ("Maya, can you ...?" -> Maya) and labelled actions. Each has an id, owner, due date, priority and source.
- **Deadlines resolved from the meeting date**: `by Friday`, `tomorrow`, `next week`, `end of month`,
  `in 3 days`, `2026-12-15`.
- **Owner resolution**: first names resolve to full attendee names; ambiguous first names are left
  unassigned rather than guessed; "we/everyone/team" becomes `Team`.
- **Review notes**: warnings for missing speaker labels, unlisted speakers, no decisions, unowned tasks.
- **Outputs**: `meeting_minutes.json`, `meeting_minutes.md`, optional `follow_up_email.md`, and `log.txt`.
  Files are written atomically.

## Agents

| Agent | File | Responsibility |
|-------|------|----------------|
| Summarizer | `agents/summarizer.py` | Short/detailed extractive summary and key topics |
| Decision Extractor | `agents/decisions.py` | Finds decision sentences |
| Task Assignment | `agents/tasks.py` | Action items, owners, deadlines, priority |
| Follow-up Email | `agents/email.py` | Recap email with decisions and action items |

```
transcript -> parser -> Summarizer -> Decision Extractor -> Task Assignment -> Follow-up Email
                                                                   |
                                  meeting_minutes.json / .md, follow_up_email.md
```

## Requirements

- Python 3.10 or newer
- No third-party packages (see `requirements.txt`)

## Usage

Interactive (asks for anything you did not pass as a flag):

```bash
python main.py
```

Non-interactive:

```bash
python main.py --topic "Q4 Launch Sync" --attendees "Maya Rao, Sam Lee, Priya Nair" \
    --transcript-file sample_transcript.txt --date 2026-11-21 --detail detailed --organizer "Maya Rao"
```

| Flag | Meaning |
|------|---------|
| `--topic` | meeting topic (required unless asked interactively) |
| `--attendees` | comma-separated names |
| `--transcript-file` | UTF-8 transcript file (otherwise paste it, ending with a line `END`) |
| `--detail short\|detailed` | summary length (default `short`) |
| `--assign-tasks / --no-assign-tasks` | assign owners (default: yes if attendees are given) |
| `--email / --no-email` | write the follow-up email (default: yes) |
| `--organizer` | name signed on the email |
| `--date YYYY-MM-DD` | meeting date used to resolve "Friday", "tomorrow" ... (default: today) |
| `--output-dir` | where outputs and `log.txt` go (default: current folder) |

`python -m meeting_assistant ...` works the same way. Exit code is `0` on success, `1` on input or file errors.

### Transcript example

```
[00:01:45] Maya: Agreed. Sam will redesign the onboarding flow by Friday.
[00:02:30] Priya: I will update the launch checklist and share it tomorrow.
[00:03:45] Priya: Action: Alex to prepare the customer announcement ASAP.
```

A full example is in `sample_transcript.txt`.

## Project structure

```
ai_meeting_assistant/
├── main.py                    # entry point
├── sample_transcript.txt
├── requirements.txt
├── log.txt
├── meeting_assistant/
│   ├── cli.py                 # argparse + interactive prompts
│   ├── models.py              # MeetingInput + validators
│   ├── parser.py              # transcript -> attributed sentences
│   ├── dates.py               # deadline phrase resolution
│   ├── workflow.py            # runs the agents, writes outputs
│   ├── render.py              # Markdown minutes + console output
│   ├── storage.py             # atomic file writes / safe reads
│   ├── logging_setup.py
│   └── agents/                # summarizer, decisions, tasks, email
└── tests/                     # unittest suite (85 tests)
```

## Testing

```bash
python -m unittest discover -s tests -v
```

Tests use fixed dates and temporary folders, so they are deterministic and never touch your real outputs.
Optional coverage: `pip install coverage && coverage run -m unittest discover -s tests && coverage report`.

## Limitations

- English only; owners and tasks are inferred from wording, so unusual phrasing can be missed or misread.
- The summary is extractive (it selects sentences; it does not paraphrase).
- Speaker labels must look like `Name:` with capitalised words (up to three).
- "next Friday" means the Friday of the following week when the next Friday falls in the current week.

## Changelog

- **2.0.0** - New transcript parser (speakers, timestamps, labels), relevance-ranked summary and key topics,
  negation-aware decisions, tasks with owners/deadlines/priority/source, Markdown minutes, review warnings,
  CLI flags plus interactive mode, atomic writes, logging and an 85-test suite. Fixed: unusable "Unassigned"
  for first-person commitments, blanket keyword matching ("will" anywhere), and a crash on missing transcript files.
- **1.0.0** - Initial four-agent demo.
