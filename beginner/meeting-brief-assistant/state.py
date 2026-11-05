"""Shared data objects.

Parallel agents get a read-only MeetingContext and RETURN their own result.
Only the orchestrator writes into MeetingState, after the agents finish, so
two threads never modify the same object.
"""
from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class MeetingContext:
    company: str
    topic: str
    category: str       # "ai_integration" | "generic"
    time_label: str


@dataclass
class MeetingState:
    request: str
    company: Optional[str] = None
    time_label: Optional[str] = None
    time_minutes: Optional[int] = None
    topic: Optional[str] = None
    category: str = "generic"
    tech: dict = field(default_factory=dict)        # Agent A result
    questions: list = field(default_factory=list)   # Agent B result
    brief: Optional[str] = None                     # Merger result
    timings: dict = field(default_factory=dict)
    wall_time: float = 0.0
    errors: list = field(default_factory=list)

    def context(self) -> MeetingContext:
        return MeetingContext(self.company or "the other team",
                              self.topic or "general discussion",
                              self.category,
                              self.time_label or "time to be confirmed")
