"""Shared helper: send a prompt to the model and get JSON back."""
import json
import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from your environment
MODEL = "claude-sonnet-5-5"


def ask_agent(prompt: str, max_tokens: int = 500):
    response = client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    text = "".join(
        block.text for block in response.content if block.type == "text"
    ).strip()
    text = text.replace("```json", "").replace("```", "").strip()  # remove code fences
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        raise ValueError(f"Agent did not return valid JSON:\n{text}")
