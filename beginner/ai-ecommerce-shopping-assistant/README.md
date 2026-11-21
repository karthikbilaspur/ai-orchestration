# AI E-commerce Shopping Assistant (`ai_ecommerce_shopping_assistant`)

A beginner-friendly **multi-agent orchestration demo** for product discovery.
It collects what a shopper wants, researches a catalog, compares the best candidates
side by side, and gives a **recommendation it can explain**.

* **No API keys, no internet.** It runs on a small made-up local catalog (26 products, 5 categories).
* **It never buys anything.** There is no cart, checkout or payment code - a test even checks for it.
* **Standard library only.** `pytest` is optional.

---

## Quick start

```bash
cd ai_ecommerce_shopping_assistant
python main.py --demo                                   # 5 scripted scenarios, writes log.txt
python main.py --query "laptop under 1000 for coding and travel, lightweight, good battery"
python main.py --interactive                            # chat-style (also the default)
python main.py --list-catalog                           # see every sample product
python -m unittest discover -s tests -t . -v            # run the tests  (or just: pytest)
```

Requires Python 3.9+.

---

## How it works

```
                 +-----------------------+
 shopper query ->| 1 Requirement         |  "laptop under 1000 for coding"
                 |   Collector           |  -> Requirements(category, budget, needs, priorities...)
                 +-----------+-----------+  (asks follow-up questions if something key is missing)
                             v
                 +-----------------------+
                 | 2 Product Research   |  filter catalog: category, brand, min specs, budget
                 |                       |  score relevance to the shopper's needs -> shortlist
                 +-----------+-----------+
                             v
                 +-----------------------+
                 | 3 Comparison          |  side-by-side table (price, rating, key specs)
                 |                       |  marks the best / worst product in every row
                 +-----------+-----------+
                             v
                 +-----------------------+
                 | 4 Recommendation      |  score + rank, then explain: reasons for,
                 |                       |  trade-offs against, why #1 beat #2
                 +-----------------------+
```

`orchestrator.py` (`ShoppingAssistant`) runs the agents in order, passes each agent's output to the next one,
logs every step, and stops early with a helpful message if a step cannot continue
(e.g. unknown product type, nothing in budget).

| Agent | File | Input -> Output |
|---|---|---|
| Requirement Collector | `agents/requirement_collector.py` | text -> `Requirements` |
| Product Research | `agents/product_research.py` | `Requirements` + `Catalog` -> `ResearchResult` |
| Comparison | `agents/comparison.py` | `ResearchResult` -> `ComparisonTable` |
| Recommendation | `agents/recommendation.py` | all of the above -> `Recommendation` |

### The scoring (explainable by design)

Every product gets four scores between 0 and 1 and a weighted sum (weights live in `config.py`):

| Part | Weight | Meaning |
|---|---|---|
| fit | 0.35 | share of the shopper's stated needs the product is tagged for |
| quality | 0.25 | customer rating / 5 |
| value | 0.20 | cheapest shortlisted price / this product's price |
| priority | 0.20 | how well it does on specs the shopper stressed ("lightweight", "good battery"...) |

Parts that do not apply (e.g. *fit* when no needs were given) are dropped and the rest re-scaled.
The report prints the parts for each product, a list of **+ reasons** and **- trade-offs**, and a sentence on why #1 beat #2.

### Design choices (and why)

* **Rule-based agents instead of an LLM** - the demo is deterministic, free, offline and easy to unit-test.
  Each agent has one clear `run()` method, so swapping one for an LLM-powered version later changes one file.
* **Plain dataclasses between agents** (`models.py`) - you can see exactly what each agent hands over.
* **Soft vs hard filters** - category, minimum specs and budget are hard; brand is ignored if it would leave nothing,
  and the budget is stretched by 20% once (with a note) before giving up.
* **Honest output** - if a match is weak, over budget, or the budget was stretched, the report says so.

---

## Project layout

```
ai_ecommerce_shopping_assistant/
├── main.py                      CLI: --demo, --query, --interactive, --list-catalog
├── README.md
├── requirements.txt
├── log.txt                      step-by-step log from a demo run
├── conftest.py                  lets pytest find the package
├── shopping_assistant/
│   ├── config.py                weights, shortlist size, currency, disclaimer
│   ├── models.py                dataclasses passed between agents
│   ├── catalog.py               sample products + spec metadata + Catalog class
│   ├── orchestrator.py          ShoppingAssistant: runs the 4 agents in order
│   ├── formatting.py            text tables / report rendering
│   ├── logging_config.py        writes agent steps to log.txt
│   └── agents/
│       ├── base.py
│       ├── requirement_collector.py
│       ├── product_research.py
│       ├── comparison.py
│       └── recommendation.py
└── tests/                       100 unit tests (unittest style, pytest-compatible)
    ├── helpers.py
    ├── test_catalog.py
    ├── test_requirement_collector.py
    ├── test_product_research.py
    ├── test_comparison.py
    ├── test_recommendation.py
    ├── test_formatting.py
    ├── test_orchestrator.py     end-to-end, "never buys", logging
    └── test_results.txt         saved output of the last test run
```

## Example

```
$ python main.py --query "running shoes for a marathon, cushioned, max 200"

=== 1. Requirements (Requirement Collector) ===
Category: running shoes | Budget: up to $200 | Needs: running, marathon | Priorities: cushion
...
=== 4. Recommendation (Recommendation agent) ===
#1 <top pick> - score NN/100
     + Matches what you asked for: ...
     - <trade-off>
Why the top pick: <top pick> beats <runner-up> by N points, mainly because ...
```
(Run `python main.py --demo` or open `log.txt` to see full real output.)

## What the Requirement Collector understands

* **Product type** - laptop, headphones/earbuds, smartphone, running shoes, backpack (`laptop bag` -> backpack: last noun wins)
* **Budget** - `under 1000`, `below $1,200`, `max 200`, `budget of 1.5k`, `between 500 and 800`, `at least $300`
  (numbers followed by units like `1.5 kg` or `16gb` are *not* mistaken for prices)
* **Needs** - coding, gaming, student, travel, office, creative, music, wireless, noise-cancelling, gym, running, marathon, trail, hiking, ...
* **Priorities** - battery, lightweight, camera, storage, performance, cushioning, capacity, durability, value
* **Hard specs** - `16GB RAM`, `1TB SSD`, `12 hours battery`
* **Brands** - any brand in the catalog

## Extending it

* **Add products** - append `_p(...)` lines to `SAMPLE_PRODUCTS` in `catalog.py` (tests check each product has every spec).
* **Add a category** - add it to `CATEGORY_SPECS`, `CATEGORY_LABELS`, `PRIORITY_SPECS`, and `CATEGORY_KEYWORDS`.
* **Change what matters** - edit `SCORE_WEIGHTS` in `config.py`.
* **Use an LLM** - subclass/replace `RequirementCollectorAgent.parse()` to call a model, keep returning `Requirements`.

## Known limitations

* Keyword matching, not real language understanding ("something lightweight-ish" works; sarcasm does not).
* One category per request; prices are made up and in a single currency (`CURRENCY` in `config.py`).
* Only the top 3 shortlisted products are compared and ranked.

## Challenge checklist

- [x] Requirement Collector agent (parses text, asks follow-ups)
- [x] Product Research agent (filters + relevance over a local catalog)
- [x] Comparison agent (side-by-side table with winners per row)
- [x] Recommendation agent (ranked, explainable)
- [x] Local sample catalog, no API keys
- [x] Never buys anything
- [x] Unit tests, README, requirements.txt, log.txt
