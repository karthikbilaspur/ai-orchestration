"""Data contracts between agents. Each agent has ONE output type."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class TopicRequest:
    topic: str
    audience: str = "general readers"
    tone: str = "helpful, clear"
    format: str = "blog"  # blog | linkedin | newsletter | twitter-thread
    length: str = "medium"  # short | medium | long
    threshold: int = 80
    max_loops: int = 3

@dataclass
class ResearchBrief:
    topic: str
    key_points: List[str] = field(default_factory=list)
    angles: List[str] = field(default_factory=list)
    audience_questions: List[str] = field(default_factory=list)
    stats_to_verify: List[str] = field(default_factory=list)
    suggested_outline: List[str] = field(default_factory=list)
    raw_llm_output: str = ""

@dataclass
class Draft:
    title: str
    body: str
    version: int = 1
    word_count: int = 0
    def __post_init__(self):
        self.word_count = len(self.body.split())

@dataclass
class SEOPlan:
    primary_keyword: str = ""
    secondary_keywords: List[str] = field(default_factory=list)
    headings: List[str] = field(default_factory=list)
    meta_title: str = ""
    meta_description: str = ""
    internal_link_ideas: List[str] = field(default_factory=list)
    keyword_density_notes: str = ""

@dataclass
class Review:
    clarity: int = 0
    structure: int = 0
    depth: int = 0
    seo_fit: int = 0
    tone_fit: int = 0
    issues: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    @property
    def overall(self) -> float:
        return round(0.25*self.clarity + 0.20*self.structure + 0.25*self.depth + 0.15*self.seo_fit + 0.15*self.tone_fit, 1)
    @property
    def passed(self) -> bool:
        return self.overall >= 80  # overridden by orchestrator threshold check

@dataclass
class FinalContent:
    request: TopicRequest
    brief: ResearchBrief
    draft: Draft
    seo: SEOPlan
    review: Review
    loops_used: int = 0
    history: List[dict] = field(default_factory=list)
    def to_markdown(self) -> str:
        lines = [f"# {self.draft.title}", "", f"> Audience: {self.request.audience} | Tone: {self.request.tone} | Format: {self.request.format}", f"> Quality Score: **{self.review.overall}/100** (after {self.loops_used} revision loop(s))", "", self.draft.body, "", "---", "", "## SEO", f"- **Primary keyword:** {self.seo.primary_keyword}", f"- **Secondary:** {', '.join(self.seo.secondary_keywords)}", f"- **Meta title:** {self.seo.meta_title}", f"- **Meta description:** {self.seo.meta_description}", "", "## Review Notes", f"- Strengths: {', '.join(self.review.strengths) or '—'}", f"- Issues fixed: {', '.join(self.review.issues) or '—'}"]
        return "\n".join(lines)
