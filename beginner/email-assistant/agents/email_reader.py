"""Agent 1: reads the raw email and extracts key information."""
from agents.llm import ask_agent


def email_reader(email: dict[str, str]):
    prompt = f"""
ROLE:
You are the Email Reader agent for an online laptop store.

TASK:
Read the customer email below and extract the key information.
Do not classify, solve, or reply. Only extract.

RULES:
- Use only information that is in the email.
- If something is missing, write "not provided". Never guess.
- Keep the issue summary to one sentence.
- Return only the JSON. No explanation, no code fences.

EMAIL:
From: {email['sender']}
Subject: {email['subject']}
Body: {email['body']}

OUTPUT (JSON only):
{{
  "customer_email": "",
  "order_id": "",
  "product_price": "",
  "issue_summary": "",
  "customer_request": "",
  "urgency": "low | medium | high"
}}
"""
    return ask_agent(prompt)
