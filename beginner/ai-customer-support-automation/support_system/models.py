from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class CustomerCase:
    issue: str
    started_when: str
    product_impact: str
    troubleshooting_tried: str
    wants_human: bool


@dataclass
class Classification:
    category: str
    confidence: str
    reason: str


@dataclass
class Priority:
    level: str
    score: int
    reason: str


@dataclass
class Resolution:
    summary: str
    steps: list[str]
    needs_customer_confirmation: bool = True


@dataclass
class Escalation:
    required: bool
    reason: str
    handoff_queue: str


@dataclass
class SupportReport:
    case: CustomerCase
    classification: Classification
    priority: Priority
    resolution: Resolution
    escalation: Escalation

    def to_dict(self) -> dict[str, Any]:
        return {
            "case": asdict(self.case),
            "classification": asdict(self.classification),
            "priority": asdict(self.priority),
            "resolution": asdict(self.resolution),
            "escalation": asdict(self.escalation),
        }
