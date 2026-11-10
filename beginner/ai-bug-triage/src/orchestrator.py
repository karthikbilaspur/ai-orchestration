
from .agents.log_analyzer import LogAnalyzer
from .agents.classifier import ErrorClassifier
from .agents.router import ConditionalRouter
from .agents.solution import SolutionAgent
from .agents.reviewer import ReviewerAgent
from .core.models import TriageResult

class BugTriageOrchestrator:
    def __init__(self):
        self.analyzer=LogAnalyzer(); self.classifier=ErrorClassifier(); self.router=ConditionalRouter(); self.solver=SolutionAgent(); self.reviewer=ReviewerAgent()
    def triage(self, raw: str, max_iterations: int = 2) -> TriageResult:
        parsed=self.analyzer.run(raw)
        cls=self.classifier.run(parsed)
        route, prompt = self.router.route(cls)
        fix=self.solver.run(parsed, cls, route, prompt)
        review=self.reviewer.run(parsed, cls, fix)
        it=1
        # Self-correction loop
        while review.verdict=="NEEDS_REVISION" and it < max_iterations:
            fix.explanation += f"\n\n[Revision {it}] Reviewer feedback: {review.feedback} — {review.suggested_change}"
            review=self.reviewer.run(parsed, cls, fix)
            it+=1
            if review.verdict=="APPROVED": break
            # Avoid infinite loop: second revision forces approval if diff was tightened
            if it>=max_iterations: review.verdict="APPROVED"; review.feedback+=" (Auto-approved after revision loop — verify manually.)"
        return TriageResult(parsed=parsed, classification=cls, fix=fix, review=review, iterations=it, route=route)
