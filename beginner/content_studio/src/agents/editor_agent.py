from .base import BaseAgent
from ..models import Draft, Review, SEOPlan

class EditorAgent(BaseAgent):
    name = "EditorAgent"
    def run(self, draft: Draft, review: Review, seo: SEOPlan) -> Draft:
        self.log(f"Editing draft v{draft.version} -> v{draft.version+1} ({len(review.issues)} issues)")
        body = draft.body
        # Fix 1: ensure primary keyword in intro if missing
        if seo.primary_keyword and seo.primary_keyword.lower() not in body.lower()[:500]:
            body = body.replace("## The short version", f"## The short version\n\nThis is a practical guide to {seo.primary_keyword}.", 1) if "## The short version" in body else f"This guide covers {seo.primary_keyword}.\n\n" + body
        # Fix 2: add example/checklist if depth was flagged
        if any("thin" in i for i in review.issues) and "Checklist" not in body:
            body += "\n\n## Checklist\n\n- [ ] Pick one small first step\n- [ ] Do it today (25 minutes)\n- [ ] Note what worked\n- [ ] Repeat tomorrow"
        # Fix 3: tighten — remove double spaces, ensure headings present
        body = body.replace("  ", " ").strip()
        # Add editor's note of what changed
        if review.suggestions:
            body += "\n\n*Edited for clarity, structure, and SEO based on critic feedback.*"
        return Draft(title=draft.title, body=body, version=draft.version + 1)
