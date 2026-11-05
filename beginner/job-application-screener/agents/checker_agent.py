"""Agent 2: the gatekeeper. Pure Python rules, no LLM, so decisions are predictable.

- Python missing      -> Rejected, pipeline STOPS (Scorer never runs)
- AI/LLM missing      -> Weak Match (continues to the Scorer)
- otherwise           -> Strong Match
"""
from skills_taxonomy import category, job_requirements
from state import ScreeningState


class CheckerAgent:
    def run(self, state: ScreeningState) -> ScreeningState:
        state.required = job_requirements(state.job_description)
        state.ai_skills = [s for s in state.skills if category(s) == "ai_llm"]

        if state.required["python"] and "Python" not in state.skills:
            state.match_level = "Rejected"
            state.status, state.reason = "Rejected", "No Python skills"
            state.stopped_early = True
            return state

        if state.required["ai_llm"] and not state.ai_skills:
            state.match_level = "Weak Match"
            state.missing = ["AI/LLM"]
        else:
            state.match_level = "Strong Match"
        return state
