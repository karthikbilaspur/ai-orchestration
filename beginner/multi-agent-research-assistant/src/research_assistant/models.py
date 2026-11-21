from pydantic import BaseModel, Field, HttpUrl


class Source(BaseModel):
    source_id: str = Field(description="Stable ID such as S1")
    title: str
    url: str
    snippet: str = ""


class ResearchBundle(BaseModel):
    question: str
    sources: list[Source] = Field(default_factory=list)
    research_notes: str = ""


class EvidencePoint(BaseModel):
    claim: str
    source_ids: list[str] = Field(default_factory=list)
    confidence: str = Field(default="medium", pattern="^(low|medium|high)$")
    caveat: str = ""


class Analysis(BaseModel):
    overview: str
    key_findings: list[EvidencePoint] = Field(default_factory=list)
    disagreements: list[str] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)


class FactCheckResult(BaseModel):
    approved: bool
    issues: list[str] = Field(default_factory=list)
    checked_claims: int = 0


class ResearchRequest(BaseModel):
    question: str = Field(min_length=8, max_length=500)
    audience: str = "general reader"
    depth: str = Field(default="standard", pattern="^(concise|standard|deep)$")
    source_text: str | None = None


class ResearchReport(BaseModel):
    title: str
    executive_summary: str
    sections: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    references: list[Source] = Field(default_factory=list)
    fact_check: FactCheckResult
