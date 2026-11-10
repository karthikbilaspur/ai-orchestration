from .base import BaseAgent
from ..models import TopicRequest, Draft, ResearchBrief, SEOPlan
from ..utils import top_keywords

class SEOAgent(BaseAgent):
    name = "SEOAgent"
    def run(self, req: TopicRequest, draft: Draft, brief: ResearchBrief) -> SEOPlan:
        self.log("Building SEO plan")
        primary = " ".join(brief.topic.lower().split()[:4]) or "guide"
        kws = top_keywords(draft.body, 5)
        secondary = [k for k in kws if k not in primary][:4]
        return SEOPlan(
            primary_keyword=primary,
            secondary_keywords=secondary,
            headings=brief.suggested_outline,
            meta_title=f"{draft.title} — A Simple Guide for {req.audience.title()}",
            meta_description=f"Learn {brief.topic} step by step. Clear, practical, and beginner-friendly — start today.",
            internal_link_ideas=["Link to your related beginner guide", "Link to your tools / resources page", "Link to a case study"],
            keyword_density_notes="Aim for primary keyword in title, first 100 words, one H2, and meta. Keep density ~1-2% — no stuffing.",
        )
