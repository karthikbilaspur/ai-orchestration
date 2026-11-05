"""Agent B (parallel): 5 smart questions, each with a one-line 'why it matters'."""
import json
import re
import time

import config
from llm import LLMClient
from state import MeetingContext

AI_BANK = [
    ("Which one or two workflows at {company} should AI improve first, and how will you measure success (cost, speed, conversion)?",
     "Forces a concrete, measurable first use case instead of vague AI ambition."),
    ("How ready is your data for this: where does it live, who owns it, and how fresh is it?",
     "Most AI projects stall on data access and quality, not on the model."),
    ("How would AI features plug into your existing services and event pipelines without hurting latency or reliability at peak load?",
     "Shows whether the integration is a quick add-on or a deep re-architecture."),
    ("Build vs buy: will you use hosted model APIs, open-source models or in-house ones, and what are your privacy and compliance limits?",
     "Decides cost, control, and what data is allowed to leave their systems."),
    ("Who owns rollout and monitoring (accuracy, hallucinations, cost per request), and what is the fallback when the model is wrong?",
     "Reveals whether there is an owner and a safety net, which predicts success."),
]

GENERIC_BANK = [
    ("What does a successful outcome for {topic} look like for {company}, and by when?",
     "Aligns everyone on the goal and the deadline."),
    ("What constraints (budget, timeline, tools, policies) should we plan around?",
     "Surfaces blockers before you promise anything."),
    ("Who are the decision makers and the day-to-day owners on your side?",
     "Tells you who to convince and who to work with."),
    ("What has been tried before on {topic}, and what went wrong?",
     "Avoids repeating past mistakes."),
    ("What is the single next step and who owns it after this call?",
     "Turns the meeting into action."),
]

PROMPT = (
    "Write exactly 5 smart questions to ask in a meeting. Reply with ONLY a JSON list of 5 objects "
    '{"q": "...", "why": "..."}. Each q must end with a question mark; each why is one short sentence.'
)


class QuestionsAgent:
    name = "QuestionsAgent"

    def __init__(self, llm: LLMClient = None):
        self.llm = llm or LLMClient()

    def run(self, ctx: MeetingContext) -> list:
        time.sleep(config.SIMULATED_LATENCY)        # imitates a slow LLM call
        if self.llm.available:
            try:
                raw = self.llm.complete(
                    PROMPT, f"Company: {ctx.company}\nTopic: {ctx.topic}", max_tokens=700)
                items = json.loads(re.sub(r"```json|```", "", raw).strip())
                if self._valid(items):
                    return [{"q": i["q"].strip(), "why": i["why"].strip()} for i in items]
            except Exception:
                pass                                   # fall through to the bank
        return self.fallback(ctx)

    @staticmethod
    def _valid(items) -> bool:
        return (isinstance(items, list) and len(items) == 5 and all(
            isinstance(i, dict) and isinstance(i.get("q"), str) and isinstance(i.get("why"), str)
            and i["q"].strip().endswith("?") and i["why"].strip() for i in items))

    @staticmethod
    def fallback(ctx: MeetingContext) -> list:
        bank = AI_BANK if ctx.category == "ai_integration" else GENERIC_BANK
        return [{"q": q.format(company=ctx.company, topic=ctx.topic), "why": why} for q, why in bank]
