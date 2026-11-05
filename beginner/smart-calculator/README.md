# AI Smart Calculator – Multi-Step AI Orchestration

Type a math problem in plain English. An LLM turns it into calculator steps,
a Python calculator does the exact math, and the LLM explains the result.

```
"What is 15% of 2,500, and add 500 to the result?"
   -> LLM plan:   percent_of(15, 2500) -> add($1, 500)
   -> Calculator: 375 -> 875
   -> LLM explanation + final answer: 875
```

## Why split the work?
LLMs are great at understanding language but can slip on arithmetic.
So the LLM only *plans* and *explains*; Python does every calculation.

## Pipeline
1. Receive the question (`main.py`)
2. LLM reads it (`prompts/understand.txt`)
3. LLM returns operations as JSON, validated by `orchestrator.parse_plan`
4. Operations are sent to the calculator (`calculator.py`)
5. Results are collected, with `$1`-style references to earlier steps
6. LLM writes a simple explanation (`prompts/explain.txt`)
7. The final answer is displayed

Every stage is written to `log.txt`.

## Project layout
```
smart_calculator/
├── main.py            CLI (one-shot or interactive)
├── orchestrator.py    the 7-step pipeline + plan validation
├── calculator.py      safe calculator tool (no eval)
├── llm_client.py      Claude client + offline fallback
├── config.py          paths, model name
├── logger_setup.py    logging to log.txt
├── prompts/           understand.txt, explain.txt
├── tests/             pytest unit tests (no network needed)
├── log.txt            run log
├── requirements.txt
└── README.md
```

## Setup
```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY="your-key"     # Windows: set ANTHROPIC_API_KEY=your-key
```
Without a key the app uses a limited **offline mode** (simple phrases such as
"15% of 2,500 then add 500" or "12 times 7 minus 4") so you can still try it.

## Run
```bash
python main.py "What is 15% of 2,500, and add 500 to the result?"
python main.py            # interactive mode
```

## Test
```bash
pytest -v
```

## Supported operations
add, subtract, multiply, divide, percent_of, power, sqrt, modulo.
To add one, put it in `OPERATIONS` in `calculator.py` and list it in
`prompts/understand.txt`.

## Ideas to extend
- Add `average`, `round`, or unit conversions
- Build a Streamlit front end
- Add retry when the LLM returns invalid JSON
