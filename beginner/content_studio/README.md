# Project 19 — AI Content Creation & Review Studio

**Time:** 2–3 hours | **Pattern:** Multi-agent collaboration + iterative refinement

Enter a topic → get ready-to-publish content.

## Flow

```
Topic
  |
Research Agent  → key points, angles, sources, audience questions
  |
Writer Agent    → first draft
  |
  +------ SEO Agent → keywords, headings, meta, internal links
  |
Critic Agent    → readability + quality score (0-100)
  |
Quality Score
  |
Below Threshold? (default 80)
  | Yes
Editor / Rewrite → improves draft, loops back to Critic (max 3 loops)
  | No
Final Content
```

## Quick Start

```bash
pip install -r requirements.txt
python -m src.main --topic "How to start a rooftop garden in a city" --audience "beginners" --tone "friendly"
python -m src.main --topic "AI agents for small businesses" --format blog --length medium --interactive
```

## Project Structure

```
project19_ai_content_studio/
├── README.md
├── requirements.txt
├── log.txt
├── src/
│   ├── __init__.py
│   ├── main.py                 # CLI + orchestration entrypoint
│   ├── orchestrator.py         # Pipeline, loop, threshold logic
│   ├── models.py               # Dataclasses: TopicRequest, Draft, Review, FinalContent
│   ├── utils.py                # Readability, keyword helpers
│   └── agents/
│       ├── __init__.py
│       ├── base.py             # BaseAgent + LLM provider abstraction
│       ├── research_agent.py
│       ├── writer_agent.py
│       ├── seo_agent.py
│       ├── critic_agent.py
│       └── editor_agent.py
├── examples/
│   └── sample_output.md        # Example run
└── tests/
    ├── __init__.py
    ├── test_agents.py          # Unit tests for each agent
    ├── test_orchestrator.py    # Pipeline + loop tests
    ├── test_utils.py           # Readability / SEO helpers
    └── test_integration.py     # End-to-end test
```

## Agents

| Agent | Input | Output | What it does |
|---|---|---|---|
| **1. Topic Research** | Topic, audience | `ResearchBrief` | Key points, angles, questions, stats to verify, outline |
| **2. Content Writer** | Brief | `Draft` | First draft in requested tone/format |
| **3. SEO Agent** | Draft + Brief | `SEOPlan` | Primary/secondary keywords, H2/H3s, meta title/description, links |
| **4. Critic Agent** | Draft + SEO | `Review` | Scores: clarity, structure, depth, SEO, tone. Overall 0-100 + issues |
| **5. Editor Agent** | Draft + Review + SEO | `Draft` v2 | Fixes issues, tightens, applies SEO without keyword stuffing |

## Quality Scoring

Critic scores 5 dimensions (0-100 each, weighted):
- Clarity / Readability: 25%
- Structure / Flow: 20%
- Depth / Usefulness: 25%
- SEO Fit: 15%
- Tone / Audience Fit: 15%

`overall = weighted average`. Threshold default `80`. Max `3` revision loops.

## LLM Providers

Works **without any API key** using the built-in `MockProvider` (template-based, great for learning/testing).
Plug in a real LLM by setting env vars:

```bash
# OpenAI-compatible
export LLM_PROVIDER=openai
export OPENAI_API_KEY=sk-...
export OPENAI_MODEL=gpt-4o-mini

# Or Anthropic
export LLM_PROVIDER=anthropic
export ANTHROPIC_API_KEY=...
```

See `src/agents/base.py` for `LLMProvider` interface. Implement `generate(prompt) -> str` to add your own.

## CLI Options

| Flag | Default | Description |
|---|---|---|
| `--topic` | required | Topic to write about |
| `--audience` | `general readers` | Who it's for |
| `--tone` | `helpful, clear` | Voice |
| `--format` | `blog` | `blog` / `linkedin` / `newsletter` / `twitter-thread` |
| `--length` | `medium` | `short` / `medium` / `long` |
| `--threshold` | `80` | Quality threshold to pass |
| `--max-loops` | `3` | Max editor revisions |
| `--output` | - | Save final markdown to file |
| `--interactive` | - | Step-through mode, pause after each agent |
| `--no-seo` | - | Skip SEO agent (for testing) |

## What You'll Learn

- Agent collaboration: each agent has one job, one output contract
- Quality scoring: turning subjective review into a measurable gate
- Iterative refinement: critic → editor loop until threshold or max loops
- Orchestration: state passing, logging, graceful failure

## Example Output

See `examples/sample_output.md` for a full run.
