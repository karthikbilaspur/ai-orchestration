class ClassifierAgent:
    """Classifies the complaint using keyword signals."""

    KEYWORDS = {
        "billing": {"bill", "billing", "charged", "charge", "refund", "invoice", "payment"},
        "technical": {"error", "bug", "crash", "broken", "slow", "not working", "loading", "install"},
        "account": {"login", "log in", "password", "account", "locked", "sign in", "verification"},
        "delivery": {"delivery", "shipping", "shipment", "package", "tracking", "order"},
        "product": {"feature", "product", "damaged", "defect", "quality", "missing part"},
    }

    def classify(self, issue: str):
        from support_system.models import Classification

        text = issue.lower()
        scores = {
            category: sum(1 for term in terms if term in text)
            for category, terms in self.KEYWORDS.items()
        }
        category, score = max(scores.items(), key=lambda item: item[1])
        if score == 0:
            return Classification("other", "low", "No category-specific keywords were detected.")
        confidence = "high" if score >= 2 else "medium"
        return Classification(
            category, confidence,
            f"Matched {score} keyword signal(s) for the {category} category."
        )
