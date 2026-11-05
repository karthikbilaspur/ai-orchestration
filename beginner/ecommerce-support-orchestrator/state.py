"""Shared state object passed from agent to agent."""
from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class ConversationState:
    message: str
    intent: Optional[str] = None        # order_status | refund | complaint | unknown
    sentiment: Optional[str] = None     # angry | neutral
    confidence: float = 0.0
    order_id: Optional[str] = None
    tracking: Optional[dict] = None     # {"status": ..., "link": ...}
    reply: Optional[str] = None
    escalate: bool = False              # True -> hand over to a human
    errors: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)
