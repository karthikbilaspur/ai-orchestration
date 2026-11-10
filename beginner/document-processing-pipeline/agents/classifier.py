"""Agent 2: Classification Agent — identifies document type."""
KEYWORDS = {
    "invoice": ["invoice", "invoice no", "bill to", "total due", "amount due", "tax", "gst", "payment due"],
    "contract": ["agreement", "contract", "parties", "terms and conditions", "hereby agree", "clause", "termination"],
    "resume": ["resume", "curriculum vitae", "experience", "education", "skills", "work history", "objective"],
    "receipt": ["receipt", "paid", "transaction", "thank you for your purchase", "cashier", "change due"],
    "letter": ["dear", "sincerely", "regards", "to whom it may concern"],
    "report": ["report", "executive summary", "findings", "conclusion", "methodology"],
}
class ClassificationAgent:
    def run(self, state: dict) -> dict:
        text = state["raw_text"].lower()
        scores = {k: sum(1 for w in v if w in text) for k, v in KEYWORDS.items()}
        best = max(scores, key=scores.get)
        confidence = round(scores[best] / max(1, len(KEYWORDS[best])), 2) if scores[best] else 0.0
        if scores[best] == 0:
            best, confidence = "unknown", 0.0
        return {"document_type": best, "confidence": confidence, "classification_reason": f"Matched keywords: {scores}", "classification_scores": scores}
