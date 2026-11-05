"""Agent A (parallel): 3 points about the company's current tech stack.

Order of preference: built-in researched notes -> LLM 'imagine' (clearly labelled)
-> generic assumptions (clearly labelled). The brief always says which one was used.
"""
import json
import re
import time

import config
from llm import LLMClient
from state import MeetingContext
from tools import company_profiles

IMAGINE_PROMPT = (
    "You are preparing a meeting brief. List exactly 3 short points on the likely current "
    "tech stack of the given company. Use hedged wording ('likely', 'reportedly') where unsure. "
    "Reply with ONLY a JSON list of 3 strings."
)


class TechStackAgent:
    name = "TechStackAgent"

    def __init__(self, llm: LLMClient = None):
        self.llm = llm or LLMClient()

    def run(self, ctx: MeetingContext) -> dict:
        time.sleep(config.SIMULATED_LATENCY)        # imitates a slow search / LLM call
        profile = company_profiles.lookup(ctx.company)
        if profile:
            return {"points": list(profile["points"]), "kind": "researched",
                    "origin": f"public sources, checked {profile['as_of']}: "
                              + ", ".join(profile["sources"])}
        if self.llm.available:
            try:
                raw = self.llm.complete(IMAGINE_PROMPT, ctx.company, max_tokens=300)
                points = json.loads(re.sub(r"```json|```", "", raw).strip())
                if isinstance(points, list) and len(points) == 3 and all(
                        isinstance(p, str) and p.strip() for p in points):
                    return {"points": [p.strip() for p in points], "kind": "imagined",
                            "origin": "AI-generated from model knowledge, unverified"}
            except Exception:
                pass                                   # fall through to generic
        return {
            "points": [
                f"Likely a cloud-hosted, service-based backend with APIs between teams "
                f"(assumption: ask {ctx.company} to confirm).",
                "Likely a central data warehouse or lake that feeds analytics and any ML work (assumption).",
                "Unknown how much AI is already in production: ask early what exists today vs. planned.",
            ],
            "kind": "assumed",
            "origin": f"no research notes for {ctx.company}; generic assumptions, verify in the meeting",
        }
