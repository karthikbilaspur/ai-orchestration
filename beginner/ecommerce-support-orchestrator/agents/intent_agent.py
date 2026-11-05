"""Agent 1: decide what the customer wants and how they feel."""
import json
import re
from state import ConversationState
from llm import LLMClient

VALID_INTENTS = {"order_status", "refund", "complaint", "unknown"}

REFUND_WORDS = ["refund", "money back", "return", "cancel my order", "reimburse"]
COMPLAINT_WORDS = ["complaint", "complain", "worst", "terrible", "unacceptable",
                   "scam", "disappointed", "horrible", "useless", "pathetic"]
STATUS_WORDS = ["where is", "where's", "track", "status", "not delivered",
                "delivery", "arrive", "ordered", "order"]
ANGRY_WORDS = ["still not", "worst", "terrible", "unacceptable", "ridiculous",
               "angry", "furious", "scam", "horrible", "useless", "pathetic",
               "waiting for", "!!"]

SYSTEM_PROMPT = (
    "You classify customer support messages. Reply with ONLY JSON like "
    '{"intent": "order_status|refund|complaint|unknown", '
    '"sentiment": "angry|neutral", "confidence": 0.0-1.0}. No other text.'
)


class IntentAgent:
    def __init__(self, llm: LLMClient = None):
        self.llm = llm or LLMClient()

    def run(self, state: ConversationState) -> ConversationState:
        result = None
        if self.llm.available:
            try:
                result = self._llm_classify(state.message)
            except Exception as exc:  # bad JSON, network error, etc.
                state.errors.append(f"intent LLM failed, using rules: {exc}")
        if result is None:
            result = self._rule_classify(state.message)
        state.intent = result["intent"]
        state.sentiment = result["sentiment"]
        state.confidence = result["confidence"]
        return state

    def _llm_classify(self, message: str) -> dict:
        raw = self.llm.complete(SYSTEM_PROMPT, message, max_tokens=100)
        data = json.loads(re.sub(r"```json|```", "", raw).strip())
        intent = data.get("intent", "unknown")
        sentiment = data.get("sentiment", "neutral")
        if intent not in VALID_INTENTS or sentiment not in {"angry", "neutral"}:
            raise ValueError(f"invalid classification: {data}")
        return {"intent": intent, "sentiment": sentiment,
                "confidence": float(data.get("confidence", 0.7))}

    @staticmethod
    def _rule_classify(message: str) -> dict:
        text = message.lower()
        sentiment = "angry" if any(w in text for w in ANGRY_WORDS) else "neutral"
        # Priority: refund > complaint > order_status
        if any(w in text for w in REFUND_WORDS):
            return {"intent": "refund", "sentiment": sentiment, "confidence": 0.9}
        if any(w in text for w in COMPLAINT_WORDS):
            return {"intent": "complaint", "sentiment": sentiment, "confidence": 0.85}
        if any(w in text for w in STATUS_WORDS):
            return {"intent": "order_status", "sentiment": sentiment, "confidence": 0.85}
        return {"intent": "unknown", "sentiment": sentiment, "confidence": 0.2}
