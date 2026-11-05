"""Rule-based orchestration: Parser -> Policy -> Notifier, one fixed path, every step logged."""
from agents import ParserAgent, PolicyAgent, NotifierAgent
from llm import LLMClient
from logger_setup import get_logger
from state import ExpenseState

log = get_logger()


class ExpenseOrchestrator:
    def __init__(self):
        llm = LLMClient()
        log.info("Orchestrator ready | decisions=plain rules | parser fallback=%s",
                 "LLM" if llm.available else "off")
        self.pipeline = [("ParserAgent", ParserAgent(llm)), ("PolicyAgent", PolicyAgent()),
                         ("NotifierAgent", NotifierAgent())]

    def process(self, message: str, sender: str = None, attachments: list = None,
                claim_id: str = "-") -> ExpenseState:
        state = ExpenseState(raw=message.strip(), sender=sender, attachments=list(attachments or []))
        log.info("INPUT    | id=%s sender=%s files=%d | %s", claim_id, sender, len(state.attachments), state.raw)
        for name, agent in self.pipeline:
            try:
                state = agent.run(state)
            except Exception as exc:       # never auto-approve or reject because of a crash
                log.error("%s crashed: %s", name, exc)
                state.errors.append(f"{name}: {exc}")
                state.decision, state.rule_id = "Manager Review", "ERROR"
                state.message = "Sent to manager: automatic check failed"
                state.reply = f"Hi, your expense needs manual review: {state.message}."
                break
            log.info("%-13s -> %s", name, self._summary(name, state))
        for err in state.errors:
            log.warning("note     | %s", err)
        log.info("RESULT   | %s", state.result())
        log.info("-" * 70)
        return state

    @staticmethod
    def _summary(name: str, s: ExpenseState) -> str:
        if name == "ParserAgent":
            return f"{s.parsed()} city={s.city} client={s.client_related} flags={s.flags}"
        if name == "PolicyAgent":
            return f"rule={s.rule_id} ({s.rule_description}) decision={s.decision}"
        return f"reply={s.reply}"
