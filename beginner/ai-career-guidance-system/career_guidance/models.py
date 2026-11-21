from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class LearnerProfile:
    education: str
    languages: list[str]
    interests: list[str]
    daily_hours: float
    learning_preference: str
    target: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SkillAnalysis:
    strengths: list[str] = field(default_factory=list)
    skill_gaps: list[str] = field(default_factory=list)
    transferable_skills: list[str] = field(default_factory=list)
    summary: str = ""


@dataclass
class CareerMatch:
    career: str
    score: int
    rationale: list[str]
    priority_skills: list[str]


@dataclass
class GuidanceReport:
    profile: LearnerProfile
    skill_analysis: SkillAnalysis
    career_recommendations: list[CareerMatch]
    roadmap: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "profile": self.profile.to_dict(),
            "skill_analysis": asdict(self.skill_analysis),
            "career_recommendations": [asdict(x) for x in self.career_recommendations],
            "roadmap": self.roadmap,
        }
