"""The orchestrator: runs Intent -> Info -> Reply in sequence."""
from agents import IntentAgent, InfoAgent, ReplyAgent
from llm import LLMClient
from logger_setup import get_logger
from state import ConversationState

log = get_logger()

FALLBACK_REPLY = ("Sorry, something went wrong on our side. A human teammate "
                  "will contact you shortly.")


class SupportOrchestrator:
    def __init__(self):
        llm = LLMClient()
        log.info("Orchestrator ready | mode=%s", "LLM" if llm.available else "rule-based")
        self.pipeline = [("IntentAgent", IntentAgent(llm)),
                         ("InfoAgent", InfoAgent()),
                         ("ReplyAgent", ReplyAgent(llm))]

    def handle(self, message: str) -> ConversationState:
        state = ConversationState(message=message)
        log.info("INPUT   | %s", message)
        for name, agent in self.pipeline:
            try:
                state = agent.run(state)
            except Exception as exc:
                log.error("%s crashed: %s", name, exc)
                state.errors.append(f"{name}: {exc}")
                state.escalate = True
                state.reply = FALLBACK_REPLY
                break
            log.info("%-11s -> intent=%s sentiment=%s conf=%.2f order_id=%s tracking=%s",
                     name, state.intent, state.sentiment, state.confidence,
                     state.order_id, (state.tracking or {}).get("status"))
        for err in state.errors:
            log.warning("note    | %s", err)
        log.info("REPLY   | %s", state.reply)
        log.info("ESCALATE| %s", state.escalate)
        log.info("-" * 60)
        return state
