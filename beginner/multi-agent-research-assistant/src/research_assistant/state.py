from typing import TypedDict
from .models import ResearchRequest, ResearchBundle, Analysis, FactCheckResult


class ResearchState(TypedDict, total=False):
    request: ResearchRequest
    research: ResearchBundle
    analysis: Analysis
    fact_check: FactCheckResult
    report_markdown: str
    errors: list[str]
