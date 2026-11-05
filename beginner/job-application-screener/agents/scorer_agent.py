"""Agent 3: score 1-10 and write a 2-line reason. Runs only if the Checker passed.

The score is rule-based (consistent and explainable across 200 resumes a day).
An optional LLM may only rephrase the 2-line reason.
"""
import config
from llm import LLMClient
from skills_taxonomy import affirmative, category, find_skills
from state import ScreeningState

REASON_PROMPT = ("Write exactly 2 short lines (separated by a newline) explaining this hiring "
                 "decision. Use only the facts given. No extra text.")


class ScorerAgent:
    def __init__(self, llm: LLMClient = None):
        self.llm = llm or LLMClient()

    def run(self, state: ScreeningState) -> ScreeningState:
        score, breakdown = self._score(state)
        if state.match_level == "Weak Match":
            score = min(score, config.WEAK_MATCH_CAP)
        state.score = max(1, min(10, score))
        state.score_breakdown = breakdown
        self._decide(state)
        state.reason_lines = self._reason_lines(state)
        return state

    # ---- scoring -----------------------------------------------------
    @staticmethod
    def _score(s: ScreeningState):
        b = {"base": 1}
        if "Python" in s.skills:
            b["python"] = 2
        if s.ai_skills:
            b["ai_llm_skill"] = 3
        if len(s.ai_skills) >= 2:
            b["multiple_ai_skills"] = 1
        has_project = bool(s.sections.get("projects")) or \
            affirmative(r"\b(?:project|built|made|developed|created)\b", s.resume)
        if has_project:
            b["has_project"] = 1
        relevant = [k for k in s.skills if category(k) == "relevant"]
        if relevant:
            b["relevant_skills"] = 2 if len(relevant) >= 3 else 1
        if affirmative(r"\b(?:intern|internship)\b", s.resume):
            b["internship"] = 1
        evidence = " ".join(s.sections.get(k, "") for k in ("projects", "experience")).strip() or s.resume
        found, _ = find_skills(evidence)
        if has_project and any(category(k) == "ai_llm" for k in found):
            b["hands_on_ai"] = 1
        return sum(b.values()), b

    # ---- decision ----------------------------------------------------
    @staticmethod
    def _decide(s: ScreeningState):
        gap = " and ".join(s.missing)
        if s.match_level == "Weak Match":
            if s.score >= config.REVIEW_SCORE:
                s.status, s.reason = "Weak Match", f"No {gap} skills, but solid profile; needs human review"
            else:
                s.status, s.reason = "Rejected", f"No {gap} skills"
        elif s.score >= config.SHORTLIST_SCORE:
            s.status, s.reason = "Shortlisted", "Meets all required skills with hands-on work"
        elif s.score >= config.REVIEW_SCORE:
            s.status, s.reason = "Review", "Meets requirements but limited hands-on evidence"
        else:
            s.status, s.reason = "Rejected", "Low overall score"

    # ---- 2-line reason -----------------------------------------------
    def _reason_lines(self, s: ScreeningState) -> list:
        keep = [k for k in s.skills if category(k) in ("python", "ai_llm", "relevant")]
        project = "has project experience" if "has_project" in s.score_breakdown else "no project evidence"
        line1 = f"Relevant skills: {', '.join(keep) or 'none'}; {project}."
        gap = " and ".join(s.missing)
        line2 = {
            "Shortlisted": "Matches the requirements with hands-on evidence; recommend interview.",
            "Review": "Meets requirements but evidence is thin; needs a human look.",
            "Weak Match": f"Missing {gap}; worth a human look only if the pool is small.",
        }.get(s.status, f"Missing {gap}, which the role requires." if gap
              else "Overall evidence is too thin for this role.")
        lines = [line1, line2]

        if self.llm.available:
            try:
                facts = (f"status={s.status}, score={s.score}/10, skills={s.skills}, "
                         f"missing={s.missing}, job={s.job_description}")
                raw = self.llm.complete(REASON_PROMPT, facts, max_tokens=120) or ""
                got = [ln.strip() for ln in raw.splitlines() if ln.strip()]
                if len(got) == 2:
                    lines = got
            except Exception as exc:
                s.errors.append(f"reason LLM failed, using template: {exc}")
        return lines
