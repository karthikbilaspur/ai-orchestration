from dataclasses import dataclass, field, asdict
from typing import List

@dataclass
class Claim:
    text: str
    source: str = ""
    evidence: str = ""
    verdict: str = "UNVERIFIED"  # SUPPORTED | PARTIALLY SUPPORTED | UNSUPPORTED | CONTRADICTED
    confidence: float = 0.0
    reasoning: str = ""

@dataclass
class ResearchResult:
    question: str
    title: str
    summary: str
    subtopics: List[str]
    claims: List[Claim]
    sources: List[str]
    confidence: float
    status: str  # PASS / PASS_WITH_WARNING / FAIL
    retries_used: int
    verification_log: List[str] = field(default_factory=list)

    def to_dict(self):
        return {**asdict(self), "claims": [asdict(c) for c in self.claims]}

    def to_markdown(self):
        lines = [f"# {self.title}\n", f"**Question:** {self.question}\n",
                 f"**Confidence:** {self.confidence:.0%} | **Status:** {self.status} | **Retries:** {self.retries_used}\n",
                 f"## Summary\n{self.summary}\n", "## Verified Claims"]
        for c in self.claims:
            icon = {"SUPPORTED":"✅","PARTIALLY SUPPORTED":"⚠️","UNSUPPORTED":"❌","CONTRADICTED":"🚫"}.get(c.verdict,"❓")
            lines.append(f"- {icon} **{c.text}**\n  - Verdict: {c.verdict} ({c.confidence:.0%}) | Source: {c.source}\n  - Evidence: \"{c.evidence}\"\n  - {c.reasoning}")
        lines.append("\n## Sources\n" + "\n".join(f"- {s}" for s in self.sources))
        if self.verification_log:
            lines.append("\n## Verification Log\n" + "\n".join(f"- {l}" for l in self.verification_log))
        return "\n".join(lines)
