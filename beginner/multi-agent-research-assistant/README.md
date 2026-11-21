# Multi-Agent Research Assistant

A beginner-friendly, production-minded starter project that turns a research question into a sourced report using a **LangGraph workflow** with four specialist stages:

1. **Researcher** — gathers web results with Tavily, or uses source material supplied by the user.
2. **Analyst** — extracts themes, evidence, caveats, and open questions.
3. **Fact checker** — checks that report claims cite known source IDs and flags claims that need stronger support.
4. **Writer** — produces a readable report with references and limitations.

The workflow is deliberately sequential and inspectable. It does not let agents silently invent sources. If no Tavily key is configured, the CLI asks for source material rather than pretending it performed live research.

## Requirements

- Python 3.10+
- An OpenAI API key for live LLM processing
- A Tavily API key for automatic web research (optional; manual source mode works without it)

## Setup

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows PowerShell:
.venv\Scripts\Activate.ps1

# 2. Install dependencies
pip install -r requirements.txt
pip install -e .

# 3. Configure environment
cp .env.example .env
# Add OPENAI_API_KEY and optionally TAVILY_API_KEY to .env
```

## Run

```bash
python -m research_assistant.cli
```

Or pass a question directly:

```bash
python -m research_assistant.cli --question "How are heat pumps changing home energy use?" --depth concise
```

For manual-source mode, use:

```bash
python -m research_assistant.cli --question "What are the benefits and risks of urban trees?" --source-file examples/urban_trees_sources.txt
```

If `TAVILY_API_KEY` is configured and no `--source-file` is passed, the researcher searches the web. If neither is available, the app prompts for source text.

## Environment variables

| Variable | Required | Description |
|---|---:|---|
| `OPENAI_API_KEY` | Yes for real LLM mode | API key used by the specialist agents |
| `OPENAI_MODEL` | No | Model name; defaults to `gpt-4.1-mini` |
| `TAVILY_API_KEY` | No | Enables web research |
| `MAX_SEARCH_RESULTS` | No | Maximum Tavily results (default `5`) |
| `LOG_LEVEL` | No | Python log level (default `INFO`) |

Never commit `.env` or API keys. The `.gitignore` excludes them.

## Architecture

```text
Question + audience + depth
          |
          v
     Researcher
  (Tavily / user sources)
          |
          v
       Analyst
 (themes + evidence map)
          |
          v
     Fact checker
 (source IDs + evidence gaps)
          |
          v
       Writer
 (report + references)
          |
          v
    Markdown report
```

LangGraph state carries structured data between nodes. Each agent has one responsibility. The graph is deterministic in its order, which makes it easier to debug and test than an unconstrained agent swarm.

## Project layout

```text
multi_agent_research_assistant/
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── run.py
├── logs/
│   └── app.log
├── reports/
├── examples/
│   └── urban_trees_sources.txt
├── src/
│   └── research_assistant/
│       ├── __init__.py
│       ├── agents.py
│       ├── cli.py
│       ├── config.py
│       ├── graph.py
│       ├── models.py
│       ├── research.py
│       └── state.py
└── tests/
    ├── conftest.py
    ├── test_agents.py
    ├── test_graph.py
    ├── test_models.py
    └── test_research.py
```

## Tests

Tests use fake model and search implementations, so they do **not** require API keys or internet access:

```bash
pip install -e ".[dev]"
pytest -q
```

## Important design choices

- **Grounding:** The researcher stores source IDs, titles, URLs, and snippets. The fact checker flags citations to unknown IDs and claims with no citations.
- **No fake research:** Without Tavily or supplied sources, the app asks for source material. It does not claim to have searched the web.
- **Structured agent outputs:** Pydantic models make handoffs explicit and validate data.
- **Replaceable dependencies:** Search and model clients are injected, so tests can use fakes.
- **Logs:** Runtime logs are written to `logs/app.log`; the project includes a starter log file.
- **Human review:** This is a research aide, not an authority. Verify important claims against the linked primary sources.

## Scope / next improvements

This is a focused 3–5 hour learning project, not a fully autonomous fact-verification system. The fact checker performs structural and evidence-reference checks; it cannot guarantee truth. Good next extensions include source-quality scoring, parallel research branches, human approval checkpoints, retries, token/cost tracking, and a small Streamlit UI.
