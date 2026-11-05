"""Agent 3: rules choose the template, an optional LLM only polishes the tone."""
import config
from state import ConversationState
from llm import LLMClient

POLISH_PROMPT = (
    "Rewrite this customer support reply to sound warm and natural. Keep every "
    "fact, the order ID and any link exactly as written. Do not add new facts "
    "or promises. Reply with the message only."
)


class ReplyAgent:
    def __init__(self, llm: LLMClient = None):
        self.llm = llm or LLMClient()

    def run(self, state: ConversationState) -> ConversationState:
        draft = self._choose_template(state)
        state.reply = self._polish(draft, state) if not state.escalate else draft
        return state

    def _choose_template(self, s: ConversationState) -> str:
        empathetic = s.intent == "complaint" or s.sentiment == "angry"

        # 1. Not sure what the customer wants -> human
        if s.intent == "unknown" or s.confidence < config.CONFIDENCE_THRESHOLD:
            s.escalate = True
            return ("Thanks for reaching out. I want to make sure you get the right "
                    "help, so I'm passing your message to a human teammate who will "
                    "reply shortly.")

        # 2. Refund -> policy
        if s.intent == "refund":
            ref = f" for order {s.order_id}" if s.order_id else ""
            return f"I'm sorry things didn't work out. Here is our refund policy{ref}: {config.REFUND_POLICY}"

        # 3. Need an order ID for anything else
        if not s.order_id:
            return ("I'm sorry for the trouble. Could you please share your Order ID "
                    "(for example SHOE123) so I can check it right away?")

        # 4. Order ID given but not found
        if not s.tracking:
            s.escalate = True
            return (f"I'm sorry, I couldn't find an order with ID {s.order_id}. "
                    "I've passed this to a human teammate who will check it for you.")

        status, link = s.tracking["status"], s.tracking["link"]

        # 5. Main case: upset customer + out for delivery
        if empathetic and status == "Out for delivery":
            return (f"Hi, I'm really sorry for the wait. I understand how frustrating "
                    f"that is. Good news: your order {s.order_id} is out for delivery "
                    f"and should reach you today. You can track it live here: {link}. "
                    "If it doesn't arrive by tonight, reply here and we'll sort it out right away.")

        # 6. Upset customer, other status
        if empathetic:
            if status == "Delayed":
                s.escalate = True
            return (f"I'm sorry about the trouble with order {s.order_id}. Its current "
                    f"status is: {status}. You can follow it here: {link}. "
                    "If you need more help, reply here and we'll look into it.")

        # 7. Calm status question
        return f"Your order {s.order_id} is currently: {status}. Track it here: {link}"

    def _polish(self, draft: str, s: ConversationState) -> str:
        if not self.llm.available:
            return draft
        try:
            polished = self.llm.complete(POLISH_PROMPT, draft)
            # Guardrail: facts must survive polishing, otherwise keep the template.
            if polished and (not s.order_id or s.order_id in polished) and \
                    (not s.tracking or s.tracking["link"] in polished):
                return polished
        except Exception as exc:
            s.errors.append(f"reply polish failed, using template: {exc}")
        return draft
