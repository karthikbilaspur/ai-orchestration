"""Shared state passed from agent to agent."""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ScreeningState:
    resume: str
    job_description: str
    candidate_name: str = "Unknown"
    sections: dict = field(default_factory=dict)
    skills: list = field(default_factory=list)
    negated: list = field(default_factory=list)      # skills the resume explicitly denies
    ai_skills: list = field(default_factory=list)
    required: dict = field(default_factory=dict)     # what the JD needs
    match_level: Optional[str] = None                # Strong Match | Weak Match | Rejected
    missing: list = field(default_factory=list)
    score: Optional[int] = None                      # stays None if the Scorer never ran
    score_breakdown: dict = field(default_factory=dict)
    reason_lines: list = field(default_factory=list)
    status: Optional[str] = None
    reason: Optional[str] = None
    stopped_early: bool = False
    errors: list = field(default_factory=list)

    def result(self) -> dict:
        """The final output required by the task."""
        return {"status": self.status, "reason": self.reason}

    def full(self) -> dict:
        return {
            "name": self.candidate_name,
            "status": self.status,
            "reason": self.reason,
            "score": self.score,
            "match_level": self.match_level,
            "skills": self.skills,
            "negated": self.negated,
            "reason_lines": self.reason_lines,
            "scorer_ran": self.score is not None,
        }
