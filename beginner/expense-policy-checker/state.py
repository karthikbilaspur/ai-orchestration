"""Shared state passed from agent to agent."""
from dataclasses import dataclass, field
from typing import Optional

APPROVED = "Approved"
REJECTED = "Rejected"
MANAGER = "Manager Review"
NEED_INFO = "Need More Info"


def money(value) -> str:
    return str(int(value)) if float(value).is_integer() else f"{value:.2f}"


@dataclass
class ExpenseState:
    raw: str
    sender: Optional[str] = None
    attachments: list = field(default_factory=list)
    # --- Parser Agent output
    amount: Optional[float] = None
    amounts_found: list = field(default_factory=list)
    currency: str = "INR"
    category: str = "other"
    bill: str = "Unknown"               # Yes | No | Unknown
    place: Optional[str] = None
    city: Optional[str] = None
    client_related: bool = False
    flags: list = field(default_factory=list)
    # --- Policy Agent output
    decision: Optional[str] = None
    rule_id: Optional[str] = None
    rule_description: Optional[str] = None
    message: Optional[str] = None       # the policy line (the task's required output)
    # --- Notifier Agent output
    reply: Optional[str] = None         # friendly full reply to send to the employee
    errors: list = field(default_factory=list)

    def result(self) -> dict:
        """Final output required by the task."""
        return {"decision": self.decision, "message": self.message}

    def parsed(self) -> dict:
        return {"Amount": None if self.amount is None else money(self.amount),
                "Category": self.category, "Bill": self.bill, "Place": self.place}

    def full(self) -> dict:
        return {"decision": self.decision, "message": self.message, "rule": self.rule_id,
                "amount": self.amount, "currency": self.currency, "category": self.category,
                "bill": self.bill, "place": self.place, "city": self.city,
                "sender": self.sender, "flags": self.flags, "reply": self.reply}
