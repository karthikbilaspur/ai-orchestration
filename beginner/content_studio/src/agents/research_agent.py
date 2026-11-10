from .base import BaseAgent
from ..models import TopicRequest, ResearchBrief

class ResearchAgent(BaseAgent):
    name = "ResearchAgent"
    def run(self, req: TopicRequest) -> ResearchBrief:
        self.log(f"Researching '{req.topic}' for {req.audience}")
        topic = req.topic
        # Mock mode: structured synthesis. With a real LLM, replace with llm.generate() + parsing.
        brief = ResearchBrief(
            topic=topic,
            key_points=[
                f"What {topic} actually means — in plain language",
                f"Why it matters now for {req.audience}",
                "The 3-5 steps / ideas that matter most",
                "Common mistakes and how to avoid them",
                "A concrete example / mini case study",
            ],
            angles=["Beginner guide", "Myths vs reality", "Step-by-step playbook", "Cost / time / effort breakdown"],
            audience_questions=[f"How do I start with {topic}?", f"How much does {topic} cost / take?", f"What mistakes should I avoid in {topic}?"],
            stats_to_verify=["[VERIFY] Any stat you cite — add source + year before publishing"],
            suggested_outline=["Hook + promise", "What it is / why it matters", "Step-by-step", "Mistakes to avoid", "Checklist / Next step"],
            raw_llm_output=f"Mock research for: {topic}",
        )
        return brief
