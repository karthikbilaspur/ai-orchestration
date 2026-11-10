# Project 18 — AI SQL Query Assistant

**Time:** 2–3 hours | **Focus:** Tool-calling orchestration

Ask database questions in plain English. Example:

> "What are the top 5 highest-selling products?"

## Architecture

```
Natural Language
       |
Query Understanding Agent
       |
SQL Generator Agent
       |
SQL Validator Agent
       |
Read-only DB Tool (SQLite)
       |
Explanation Agent
       |
    Result
```

### Agents

| Agent | File | Responsibility |
|---|---|---|
| 1. Query Understanding | `agents/query_understanding.py` | Parse intent, entities, limit, sort, filters |
| 2. SQL Generator | `agents/sql_generator.py` | Generate parameterized SQL from parsed intent |
| 3. SQL Validator | `agents/sql_validator.py` | Allow-list SELECT only, block mutations, check syntax + tables/columns |
| 4. Database Agent | `agents/database_agent.py` | Execute read-only queries on SQLite, timeout + row cap |
| 5. Explanation Agent | `agents/explanation_agent.py` | Summarize results in plain English |

Orchestrator: `orchestrator.py` wires the chain and logs every step.

## Quick Start

```bash
pip install -r requirements.txt
python main.py --question "What are the top 5 highest-selling products?"
python main.py --question "Show total revenue by category"
python main.py --question "Which customers spent more than 5000?"
python main.py --interactive
```

## Safety Rules (Validator)

- Only `SELECT` / `WITH ... SELECT` allowed
- Blocked keywords: INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, TRUNCATE, REPLACE, GRANT, PRAGMA, ATTACH, VACUUM
- No multiple statements (`;` + second statement), no comments that hide SQL
- Only known tables/columns from schema
- `LIMIT` enforced (default 20, max 100)
- All values parameterized — never string-interpolated user input

## Schema (SQLite, seeded in `data/sample.db`)

- `products(id, name, category, price, stock)`
- `customers(id, name, city, email)`
- `orders(id, customer_id, product_id, quantity, total_amount, order_date)`
- `sales` is a view: orders JOIN products/customers

## Project Structure

```
main.py
orchestrator.py
agents/
  query_understanding.py
  sql_generator.py
  sql_validator.py
  database_agent.py
  explanation_agent.py
config.py
db_setup.py
requirements.txt
tests/
  test_query_understanding.py
  test_sql_validator.py
  test_orchestrator.py
logs/
  run.log
```

## Example Output

```
Question: What are the top 5 highest-selling products?
SQL: SELECT p.name, SUM(o.quantity) AS total_sold ... ORDER BY total_sold DESC LIMIT 5
Result: Wireless Mouse — 142 sold, ...
Explanation: Wireless Mouse is the best seller...
```

## Tests

```bash
pytest -v
pytest tests/test_sql_validator.py -v
```

## What You'll Learn

Tool calling, SQL validation, database integration, safe execution.
