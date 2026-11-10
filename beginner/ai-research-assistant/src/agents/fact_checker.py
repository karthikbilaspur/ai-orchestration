"""Agent 3: Fact Checker — checks claims against retrieved evidence."""
import re
class FactCheckerAgent:
    def check(self, claim):
        ev, txt = claim.evidence.lower(), claim.text.lower()
        if not claim.evidence or len(claim.evidence)<20:
            claim.verdict, claim.confidence = "UNSUPPORTED", 0.1
            claim.reasoning = "No usable evidence retrieved."
            return claim
        # Overlap heuristic: in production, replace with NLI model / LLM judge
        claim_words = set(w for w in re.findall(r"[a-z]+", txt) if len(w)>3)
        ev_words = set(re.findall(r"[a-z]+", ev))
        overlap = len(claim_words & ev_words) / max(1, len(claim_words))
        # Negation / contradiction signals
        if any(x in ev for x in ["no evidence", "does not", "not supported", "myth", "false"]):
            claim.verdict, claim.confidence = "CONTRADICTED", 0.2
            claim.reasoning = "Evidence contains contradicting language."
        elif overlap >= 0.7:
            claim.verdict, claim.confidence = "SUPPORTED", round(0.75+0.25*overlap,2)
            claim.reasoning = f"High keyword overlap ({overlap:.0%}) between claim and evidence."
        elif overlap >= 0.4:
            claim.verdict, claim.confidence = "PARTIALLY SUPPORTED", round(0.4+0.3*overlap,2)
            claim.reasoning = f"Partial overlap ({overlap:.0%}); evidence covers part of claim."
        else:
            claim.verdict, claim.confidence = "UNSUPPORTED", round(0.2*overlap,2)
            claim.reasoning = f"Low overlap ({overlap:.0%}); evidence does not substantiate claim."
        return claim
    def check_all(self, claims):
        return [self.check(c) for c in claims]
    def overall_confidence(self, claims):
        if not claims: return 0.0
        weights = {"SUPPORTED":1.0,"PARTIALLY SUPPORTED":0.5,"UNSUPPORTED":0.0,"CONTRADICTED":0.0}
        return sum(weights.get(c.verdict,0)*c.confidence for c in claims)/len(claims) if claims else 0.0
        # Note: normalized so SUPPORTED high-confidence claims push toward 1.0
