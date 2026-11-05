"""Agent 2: decides which category the email belongs to."""
import json
from typing import Any, Callable, cast

from agents.llm import ask_agent as _ask_agent

ask_agent = cast(Callable[..., str], _ask_agent)


def classifier(agent1_output: Any) -> str:
    prompt = f"""
ROLE:
You are the Classifier agent for an online laptop store.

TASK:
Read the extracted email data and choose ONE category.
Do not solve the problem or write a reply. Only classify.

CATEGORIES:
- delivery: order late, missing, or tracking questions
- refund: wants money back or to return a working product
- damage: product arrived broken, cracked, or defective
- product_enquiry: questions about products, prices, or specs
- other: anything that does not fit above

RULES:
- Pick exactly one category.
- Give a confidence from 0 to 1.
- If you are unsure, set confidence below 0.7.
- Return only the JSON. No explanation, no code fences.

INPUT:
{json.dumps(agent1_output, ensure_ascii=False)}

OUTPUT (JSON only):
{{
  "category": "",
  "confidence": 0.0,
  "reason": "one short sentence"
}}
"""
    return ask_agent(prompt, max_tokens=300)
