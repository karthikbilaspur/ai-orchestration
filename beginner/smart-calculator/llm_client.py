"""LLM wrappers: a real Claude client and an offline fallback for demos/tests."""
import json
import os
import re
from typing import List

import config


class AnthropicLLM:
    """Calls the Claude API. Needs ANTHROPIC_API_KEY in the environment."""

    def __init__(self, model: str | None = None):
        import anthropic  # imported here so offline mode works without the package

        self.client = anthropic.Anthropic()
        self.model = model or config.MODEL

    def complete(self, task: str, system: str, user: str) -> str:
        message = self.client.messages.create(
            model=self.model,
            max_tokens=config.MAX_TOKENS,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return "".join(b.text for b in message.content if b.type == "text")


class OfflineLLM:
    """Tiny rule-based stand-in so the project runs without an API key.

    It only understands simple chains such as
    "15% of 2,500, then add 500" or "12 times 7 minus 4".
    """

    NUM = r"(\d+(?:\.\d+)?)"
    OP_WORDS = {
        "add": "add", "plus": "add", "added": "add",
        "subtract": "subtract", "minus": "subtract",
        "multiply": "multiply", "times": "multiply", "multiplied": "multiply",
        "divide": "divide", "divided": "divide",
    }

    def complete(self, task: str, system: str, user: str) -> str:
        if task == "plan":
            return json.dumps(self._plan(user))
        return self._explain(user)

    def _plan(self, question: str) -> dict:
        text = question.lower().replace(",", "")
        steps: List[dict] = []

        m = re.search(self.NUM + r"\s*(?:%|percent)\s+of\s+" + self.NUM, text)
        if m:
            p, x = float(m.group(1)), float(m.group(2))
            steps.append({"id": 1, "op": "percent_of", "args": [p, x],
                          "description": f"{p:g}% of {x:g}"})
            rest = text[m.end():]
        else:
            m = re.search(self.NUM + r"\s*(add|plus|minus|subtract|times|multiplied|divided)"
                          r"\s*(?:by\s+)?" + self.NUM, text)
            if not m:
                return {"error": "Offline mode could not understand this. Set ANTHROPIC_API_KEY."}
            a, word, b = float(m.group(1)), m.group(2), float(m.group(3))
            op = self.OP_WORDS[word]
            steps.append({"id": 1, "op": op, "args": [a, b], "description": f"{a:g} {op} {b:g}"})
            rest = text[m.end():]

        pattern = r"(add|plus|subtract|minus|multiply|multiplied|times|divide|divided)\w*\s+(?:by\s+)?" + self.NUM
        for m in re.finditer(pattern, rest):
            op = self.OP_WORDS[m.group(1)]
            n = float(m.group(2))
            step_id = len(steps) + 1
            steps.append({"id": step_id, "op": op, "args": [f"${step_id - 1}", n],
                          "description": f"{op} {n:g} (using the previous result)"})
        return {"steps": steps}

    def _explain(self, user: str) -> str:
        data = json.loads(user.split("RESULTS:", 1)[1])
        lines = [f"Step {s['id']}: {s['description']} = {s['result']:,}" for s in data]
        lines.append(f"Final answer: {data[-1]['result']:,}")
        return "\n".join(lines)


def get_llm():
    """Use Claude if a key is available, otherwise fall back to offline mode."""
    if os.getenv("ANTHROPIC_API_KEY"):
        return AnthropicLLM()
    print("[note] ANTHROPIC_API_KEY not set - using the limited offline mode.")
    return OfflineLLM()
