"""Agent 3: checks store policy and decides the next step."""
import json
from typing import Any
from agents.llm import ask_agent


def problem_solver(agent1_output: Any, agent2_output: Any):
    prompt = f"""
ROLE:
You are the Problem Solver agent for an online laptop store.

TASK:
Using the email details and category, decide the next step.
Do not write the customer reply. Only decide.

STORE POLICY:
- Damage: replacement or refund is possible if the customer reports it
  within 7 days of delivery and sends a photo of the damage.
- Delivery: check tracking and share the status.
- Refund: allowed within 14 days for unused products.
- Product enquiry: answer from the product catalog.

RULES:
- Never promise a replacement or refund. Only recommend it.
- If proof or information is missing, list it under "missing_info".
- If the case is unclear or high value, set "needs_human" to true.
- Return only the JSON. No explanation, no code fences.

EMAIL DETAILS:
{json.dumps(agent1_output, ensure_ascii=False)}

CATEGORY:
{json.dumps(agent2_output, ensure_ascii=False)}

OUTPUT (JSON only):
{{
  "recommended_action": "",
  "missing_info": [],
  "needs_human": true,
  "notes_for_reply_writer": ""
}}
"""
    return ask_agent(prompt)
