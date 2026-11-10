"""Agent 1: Research Planner — breaks question into subtopics."""
import re
STOP = set("what how why when where is are the a an and or of to in on for with by do does did can could should is it its this that".split())
class ResearchPlanner:
    def __init__(self, max_subtopics=4): self.max_subtopics=max_subtopics
    def plan(self, question: str):
        # Keyword extraction + templated subtopics (replace with LLM call in production)
        words = [w.strip("?,.").lower() for w in re.findall(r"[A-Za-z]+", question)]
        keywords = [w for w in words if w not in STOP and len(w)>3]
        topic = " ".join(keywords[:3]) or question
        base = [f"Definition and background of {topic}",
                f"Benefits and positive effects of {topic}",
                f"Risks, limitations and criticisms of {topic}",
                f"Evidence, examples and practical implications of {topic}"]
        return base[:self.max_subtopics]
    def refine(self, question, subtopics, checked_claims):
        # On retry: focus on unsupported / low-confidence areas + add "evidence" qualifier
        weak = [c.text for c in checked_claims if c.verdict in ("UNSUPPORTED","PARTIALLY SUPPORTED","CONTRADICTED")]
        refined = [f"{s} — find stronger evidence" for s in subtopics]
        if weak:
            refined.append(f"Verify specifically: {weak[0][:80]}")
        return refined[:self.max_subtopics+1]
