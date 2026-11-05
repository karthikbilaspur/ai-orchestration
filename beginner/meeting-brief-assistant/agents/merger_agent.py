"""Final Merger Agent: combine Agent A + Agent B into a 1-page cheat-sheet."""
import datetime
import re

import config
from llm import LLMClient
from state import MeetingState

INTRO_PROMPT = ("Write a 2-sentence intro for a meeting cheat-sheet. Mention the company, the time "
                "and the topic. Max 50 words. Reply with the text only.")


class MergerAgent:
    name = "MergerAgent"

    def __init__(self, llm: LLMClient = None):
        self.llm = llm or LLMClient()

    def run(self, s: MeetingState) -> str:
        brief = self._build(s, with_why=True)
        if brief.count("\n") + 1 > config.MAX_BRIEF_LINES:     # keep it to one page
            brief = self._build(s, with_why=False)
        return brief

    # ------------------------------------------------------------------
    def _intro(self, s: MeetingState) -> str:
        ctx = s.context()
        template = (f"You are meeting the {ctx.company} team at {ctx.time_label} to discuss "
                    f"{ctx.topic}. Goal: understand where it fits in their plans, what limits them, "
                    f"and leave with one concrete next step.")
        if self.llm.available:
            try:
                text = self.llm.complete(INTRO_PROMPT, f"{ctx.company} | {ctx.time_label} | {ctx.topic}",
                                         max_tokens=120) or ""
                if ctx.company.lower() in text.lower() and len(text.split()) <= 60:
                    return " ".join(text.split())
            except Exception:
                pass
        return template

    def _build(self, s: MeetingState, with_why: bool) -> str:
        ctx = s.context()
        out = [f"# Meeting Cheat-Sheet: {ctx.company} | {ctx.time_label}",
               f"**Topic:** {ctx.topic}  |  **Prepared:** {datetime.date.today().isoformat()}",
               "", "## 1. Intro (30-second read)", self._intro(s), ""]

        out.append(f"**{ctx.company} tech snapshot**")
        if s.tech.get("points"):
            out += [f"- {p}" for p in s.tech["points"]]
            out.append(f"_Source: {s.tech['origin']}. Verify before quoting._")
        else:
            out.append("_Tech snapshot unavailable. Open by asking them to walk you through their current stack._")
        out.append("")

        out.append("## 2. Questions to ask")
        for i, item in enumerate(s.questions, 1):
            out.append(f"{i}. **{item['q']}**")
            if with_why:
                out.append(f"   _Why: {item['why']}_")
        out += ["", "## 3. Before you hang up",
                "- Confirm the owner and date of the next step."]
        return "\n".join(out)
