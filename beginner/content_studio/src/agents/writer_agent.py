from .base import BaseAgent
from ..models import TopicRequest, ResearchBrief, Draft

class WriterAgent(BaseAgent):
    name = "WriterAgent"
    def run(self, req: TopicRequest, brief: ResearchBrief, version: int = 1) -> Draft:
        self.log(f"Writing draft v{version} ({req.format}, {req.length}, tone={req.tone})")
        title = brief.topic.strip().capitalize() if brief.topic else "Untitled"
        # Build a solid first draft from the brief — real LLM would generate prose here.
        sections = []
        sections.append(f"## The short version\n\nIf you are new to {brief.topic}, here is the promise: you can get started this week, without overthinking it. This guide is written for {req.audience}, in a {req.tone} voice.")
        for i, point in enumerate(brief.key_points, 1):
            sections.append(f"## {i}. {point}\n\nStart with the simplest version of this idea. Do one small thing today, check what worked, then repeat. That loop — small action, quick check, small fix — beats a perfect plan you never start.")
        sections.append("## Mistakes to avoid\n\n- Trying to do everything at once.\n- Copying someone else's setup without adapting it to your situation.\n- Waiting until you feel 'ready'.")
        sections.append("## Your next step\n\nPick one action from this guide and do it today. Set a 25-minute timer, finish it, and note what you learned. That is how progress compounds.")
        body = "\n\n".join(sections)
        if req.length == "short":
            body = "\n\n".join(sections[:3])
        elif req.length == "long":
            body += "\n\n## FAQ\n\n**How long does it take?** Less than you think if you start small.\n\n**Do I need expensive tools?** No — start with what you have."
        return Draft(title=title, body=body, version=version)
