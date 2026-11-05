# E-Commerce Customer Support: 3-Agent Orchestration

An angry customer writes in chat. Three small agents run in sequence and produce a reply ready to send.

```
message -> [Intent Agent] -> [Info Agent] -> [Reply Agent] -> reply
```

| Agent | Job | Tech |
|---|---|---|
| Intent Agent | intent (`order_status` / `refund` / `complaint`) + sentiment | LLM if API key set, else keyword rules |
| Info Agent | extract Order ID (regex), look up mock tracking | plain Python |
| Reply Agent | rules pick the template, optional LLM polishes wording | rules + optional LLM |

## Reply rules
- complaint **or** angry + `Out for delivery` -> empathy + tracking link
- `refund` -> refund policy
- calm status question -> short status + link
- no order ID -> ask for it
- unknown order / unclear intent / delayed order -> escalate to a human

Routing lives in plain Python so behavior stays predictable. The LLM never invents facts: polished replies must still contain the order ID and link, otherwise the template is used.

## Run
```bash
pip install -r requirements.txt     # optional; core runs on stdlib only
python main.py                      # main example + samples
python main.py -m "Where is my order SHOE998?!"
pytest -q                           # tests
```
Optional LLM mode: `export ANTHROPIC_API_KEY=your_key` (model via `LLM_MODEL`).

Every step is logged to `log.txt`.

## Structure
```
main.py  orchestrator.py  config.py  state.py  llm.py  logger_setup.py
agents/ (intent_agent, info_agent, reply_agent)   tools/tracking.py (mock)
tests/test_pipeline.py   sample_messages.json   log.txt
```
