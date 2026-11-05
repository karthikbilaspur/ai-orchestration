"""Agent 3: draft the message for the employee."""
from state import ExpenseState, APPROVED, REJECTED, MANAGER, money

_HINT = {
    REJECTED: "Please resubmit with the bill attached.",
    APPROVED: "No further action needed.",
    MANAGER: "You will hear back once your manager has reviewed it.",
}


class NotifierAgent:
    def run(self, s: ExpenseState) -> ExpenseState:
        greeting = f"Hi {s.sender}," if s.sender else "Hi,"
        if s.amount is not None:
            what = s.category.replace("_", " ") + (f" at {s.place}" if s.place else "")
            subject = f"your claim of Rs {money(s.amount)} ({what})"
        else:
            subject = "your expense message"
        parts = [f"{greeting} {subject}: {s.message}."]
        hint = _HINT.get(s.decision)
        if hint:
            parts.append(hint)
        s.reply = " ".join(parts)
        return s
