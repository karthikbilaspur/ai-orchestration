"""Orchestration: Research -> Writer -> SEO -> Critic -> (Editor loop) -> Final."""
from .models import TopicRequest, FinalContent
from .agents.research_agent import ResearchAgent
from .agents.writer_agent import WriterAgent
from .agents.seo_agent import SEOAgent
from .agents.critic_agent import CriticAgent
from .agents.editor_agent import EditorAgent

class Orchestrator:
    def __init__(self, provider=None, use_seo: bool = True):
        self.research = ResearchAgent(provider)
        self.writer = WriterAgent(provider)
        self.seo_agent = SEOAgent(provider)
        self.critic = CriticAgent(provider)
        self.editor = EditorAgent(provider)
        self.use_seo = use_seo

    def run(self, req: TopicRequest, interactive: bool = False, verbose: bool = True) -> FinalContent:
        history = []
        def step(name: str):
            history.append({"step": name})
            if verbose:
                print(f"\n=== {name} ===")
            if interactive:
                input("Press Enter to continue...")

        step("1. Research Agent")
        brief = self.research.run(req)

        step("2. Writer Agent")
        draft = self.writer.run(req, brief, version=1)

        step("3. SEO Agent")
        from .models import SEOPlan
        seo = self.seo_agent.run(req, draft, brief) if self.use_seo else SEOPlan()

        loops = 0
        while True:
            step(f"4. Critic Agent (draft v{draft.version})")
            review = self.critic.run(draft, seo, threshold=req.threshold)
            if review.overall >= req.threshold or loops >= req.max_loops:
                break
            loops += 1
            step(f"5. Editor Agent — Revision {loops}")
            draft = self.editor.run(draft, review, seo)
            # Re-run SEO after edit so headings/keywords stay fresh
            if self.use_seo:
                seo = self.seo_agent.run(req, draft, brief)

        step("6. Final Content")
        final = FinalContent(request=req, brief=brief, draft=draft, seo=seo, review=review, loops_used=loops, history=history)
        if verbose:
            print(f"\nDone! Quality: {review.overall}/100 | Loops: {loops} | Words: {draft.word_count}")
        return final
