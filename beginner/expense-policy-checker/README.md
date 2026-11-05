# Expense & Policy Checker: Rule-Based AI Orchestration

Employees send bills on WhatsApp/Slack. Three agents run in a fixed order and Finance gets a decision without reading each message.

```
"Hi, spent Rs. 1200 on client dinner at Toit, Bangalore. No bill attached."
        |
 [Parser Agent]   -> Amount=1200, Category=food, Bill=No, Place=Toit
        |
 [Policy Agent]   -> rules in order, first match wins
        |
 [Notifier Agent] -> message for the employee
        v
{"decision": "Rejected", "message": "Rejected as per policy: Bill mandatory above Rs 1000"}
```

## The policy (policy_rules.py, thresholds in config.py)
| Rule | Condition | Decision |
|---|---|---|
| R1 | amount > 1000 AND bill = No | Rejected |
| R2 | amount < 500 | Approved (auto) |
| R3 | everything else | Manager Review |

Boundaries: exactly Rs 1000 without a bill goes to the manager (rule says "above"), and exactly Rs 500 is not auto-approved (rule says "below").

Safety checks that run first (R0-*), because real chat messages are messy:
- more than one amount -> Manager Review, no amount -> Need More Info, non-rupee currency -> Manager Review
- same sender, amount and place as an earlier approved/pending claim -> Manager Review (duplicate)
- amount above Rs 1000 and nothing says whether a bill exists -> Need More Info. This is an addition to the task; set `ASK_WHEN_BILL_UNKNOWN = False` in `config.py` for the strict 3-rule behaviour.

## Design notes
- **Decisions are plain code, not AI.** Money decisions must be predictable and auditable. Every decision logs the rule that fired.
- **"No bill attached" trap:** that sentence contains the words "bill attached", so denials ("no bill", "without receipt", "lost the bill") are checked before confirmations. A real attached file always counts as a bill.
- If an agent crashes, the claim goes to the manager. It is never auto-approved or rejected by accident.
- Optional LLM: only a Parser fallback when no amount can be found, and the amount must literally appear in the message.

## Run
```bash
python main.py
python main.py -m "Spent Rs 700 on lunch at Toit, no bill" --sender Ravi
python main.py -m "Dinner Rs 1200 at Toit" --attach bill.jpg
python main.py --file sample_expenses.json     # batch, writes output/decisions.csv
pytest -q
```

## Structure
```
main.py  orchestrator.py  policy_rules.py  batch.py  config.py  state.py  llm.py  logger_setup.py
agents/ (parser_agent, policy_agent, notifier_agent)   tests/test_expense.py
sample_expenses.json   log.txt   output/ (decisions.csv, results.json)
```
