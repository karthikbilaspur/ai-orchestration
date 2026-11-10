"""Agent 4: Report Agent — final report with source references."""
from src.core.models import ResearchResult
class ReportAgent:
    def generate(self, question, subtopics, claims, confidence, status, retries, log):
        supported = [c for c in claims if c.verdict=="SUPPORTED"]
        title = f"Research Report: {question[:70]}"
        if supported:
            summary = f"Based on {len(claims)} claims checked against local sources, {len(supported)} were fully supported. " + " ".join(c.text for c in supported[:3])
        else:
            summary = "No claims could be fully supported from the available sources. Treat findings as preliminary and verify with additional sources."
        if status=="PASS_WITH_WARNING":
            summary += " ⚠️ Confidence is below threshold — some claims are unverified."
        return ResearchResult(question=question, title=title, summary=summary,
                              subtopics=subtopics, claims=claims, sources=[],
                              confidence=round(confidence,3), status=status,
                              retries_used=retries, verification_log=log)
