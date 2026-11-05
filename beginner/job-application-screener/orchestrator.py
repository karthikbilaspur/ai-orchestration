"""Conditional orchestration: Extractor -> Checker -> (Scorer only if Checker passes)."""
import config
from agents import ExtractorAgent, CheckerAgent, ScorerAgent
from llm import LLMClient
from logger_setup import get_logger
from state import ScreeningState

log = get_logger()


class ScreeningOrchestrator:
    def __init__(self):
        llm = LLMClient()
        log.info("Orchestrator ready | mode=%s", "LLM-assisted" if llm.available else "rule-based")
        self.pipeline = [("ExtractorAgent", ExtractorAgent(llm)),
                         ("CheckerAgent", CheckerAgent()),
                         ("ScorerAgent", ScorerAgent(llm))]

    def screen(self, resume: str, job_description: str = None, resume_id: str = "-") -> ScreeningState:
        state = ScreeningState(resume=resume, job_description=job_description or config.DEFAULT_JD)
        log.info("INPUT    | id=%s | JD=%s | resume=%s", resume_id, state.job_description,
                 " ".join(resume.split())[:150])
        for name, agent in self.pipeline:
            try:
                state = agent.run(state)
            except Exception as exc:
                log.error("%s crashed: %s", name, exc)
                state.errors.append(f"{name}: {exc}")
                state.status, state.reason = "Needs Human Review", "Pipeline error"
                break
            log.info("%-14s -> %s", name, self._summary(name, state))
            if state.stopped_early:
                log.info("STOP     | pipeline halted after %s; remaining agents skipped", name)
                break
        for err in state.errors:
            log.warning("note     | %s", err)
        log.info("RESULT   | %s", state.result())
        log.info("-" * 70)
        return state

    @staticmethod
    def _summary(name: str, s: ScreeningState) -> str:
        if name == "ExtractorAgent":
            return f"name={s.candidate_name} skills={s.skills} denied={s.negated}"
        if name == "CheckerAgent":
            return f"requires={s.required} match={s.match_level} missing={s.missing}"
        return f"score={s.score} {s.score_breakdown} status={s.status}"
