"""Agent 4: drafts the customer reply (a human approves it before sending)."""
import json
from typing import Any

from agents.llm import ask_agent


def reply_writer(agent1_output: dict[str, Any], agent3_output: dict[str, Any]):
    prompt = f"""
ROLE:
You are the Reply Writer agent for an online laptop store.

TASK:
Write a short, professional email reply to the customer.

RULES:
- Follow the notes from the Problem Solver exactly.
- Never promise a replacement or refund unless the notes say it is approved.
- Be polite and empathetic. Keep it under 120 words.
- If information is missing, ask for it clearly.
- Sign off as "Customer Support Team".
- Return only the JSON. No explanation, no code fences.

CUSTOMER DETAILS:
{json.dumps(agent1_output, ensure_ascii=False)}

PROBLEM SOLVER DECISION:
{json.dumps(agent3_output, ensure_ascii=False)}

OUTPUT (JSON only):
{{
  "subject": "",
  "body": ""
}}
"""
    return ask_agent(prompt)
