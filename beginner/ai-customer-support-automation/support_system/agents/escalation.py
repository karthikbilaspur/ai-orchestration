class EscalationAgent:
    """Routes cases to a human queue when explicit escalation rules are met."""

    QUEUES = {
        "billing": "Billing Support",
        "technical": "Technical Support",
        "account": "Account Security and Support",
        "delivery": "Order and Delivery Support",
        "product": "Product Support",
        "other": "General Customer Support",
    }

    def decide(self, case, classification, priority, resolution):
        from support_system.models import Escalation

        reasons = []
        if case.wants_human:
            reasons.append("Customer requested a human representative.")
        if priority.level == "critical":
            reasons.append("Critical-priority cases require human review.")
        if classification.category == "account" and any(
            word in case.issue.lower() for word in ("hacked", "unauthorized", "security")
        ):
            reasons.append("Possible account compromise requires specialist review.")
        if case.troubleshooting_tried.strip().lower() in {"yes", "tried everything", "already tried"}:
            reasons.append("Customer has already attempted troubleshooting.")

        required = bool(reasons)
        return Escalation(
            required=required,
            reason=" ".join(reasons) if reasons else "No escalation trigger detected; offer the suggested steps first.",
            handoff_queue=self.QUEUES[classification.category] if required else "Self-service / Pending customer response",
        )
