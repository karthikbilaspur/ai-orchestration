class PriorityAgent:
    """Scores urgency from impact, issue wording, and how long it has persisted."""

    CRITICAL_TERMS = ("all users", "security breach", "data loss", "cannot access any")
    HIGH_TERMS = ("completely unable", "business stopped", "urgent", "outage", "blocked")

    def assess(self, case, classification):
        from support_system.models import Priority

        text = case.issue.lower()
        score = 0
        reasons = []

        if case.product_impact == "cannot use product":
            score += 4
            reasons.append("Customer cannot use the product.")
        elif case.product_impact == "major features affected":
            score += 3
            reasons.append("Major product functionality is affected.")
        elif case.product_impact == "minor inconvenience":
            score += 1
            reasons.append("Impact is limited.")

        if any(term in text for term in self.CRITICAL_TERMS):
            score += 4
            reasons.append("Potential security, data-loss, or broad-access signal.")
        elif any(term in text for term in self.HIGH_TERMS):
            score += 2
            reasons.append("Urgent or outage-related wording detected.")

        if case.started_when.lower() in {"more than a week ago", "over a week ago"}:
            score += 1
            reasons.append("Issue has persisted for more than a week.")

        if classification.category == "account" and any(
            term in text for term in ("hacked", "unauthorized", "security")
        ):
            score += 4
            reasons.append("Possible account-security concern.")

        if score >= 7:
            level = "critical"
        elif score >= 4:
            level = "high"
        elif score >= 2:
            level = "medium"
        else:
            level = "low"

        return Priority(level, score, " ".join(reasons) or "No elevated urgency signals detected.")
