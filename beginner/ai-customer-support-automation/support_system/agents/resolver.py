class ResolverAgent:
    """Suggests safe first-line support steps by complaint category."""

    PLAYBOOKS = {
        "billing": [
            "Review the invoice or transaction date and compare it with the plan or order.",
            "Check whether the charge is pending, duplicated, or associated with another account.",
            "If the charge still looks incorrect, provide the transaction reference through the official secure support channel.",
        ],
        "technical": [
            "Refresh the page or restart the application and check the service status page.",
            "Update to the latest supported version and retry the action.",
            "If the problem continues, record the exact error message, device, operating system, and steps to reproduce it.",
        ],
        "account": [
            "Use the official account-recovery or password-reset flow.",
            "Check that the sign-in email and verification method are correct.",
            "If you suspect unauthorized access, secure the email account and request an urgent security review.",
        ],
        "delivery": [
            "Check the latest tracking update and estimated delivery window.",
            "Confirm the delivery address and whether a carrier attempted delivery.",
            "If tracking has not updated or the parcel is missing, prepare the order reference for support.",
        ],
        "product": [
            "Stop using the product if there may be a safety issue or further damage.",
            "Check the setup guide and inspect the affected part without attempting unsafe repairs.",
            "Gather the order reference and a description or photo of the defect for the support team.",
        ],
        "other": [
            "Describe the expected result and what happened instead.",
            "Include any relevant error text and the steps that led to the issue.",
            "Contact the support team with the details if the issue remains unresolved.",
        ],
    }

    def resolve(self, case, classification):
        from support_system.models import Resolution

        steps = list(self.PLAYBOOKS[classification.category])
        if case.troubleshooting_tried.strip().lower() not in {"no", "none", "not yet"}:
            steps.insert(0, "Avoid repeating steps that have already failed; share what you tried and the result.")
        return Resolution(
            summary=f"Suggested first-line guidance for your {classification.category} issue.",
            steps=steps,
            needs_customer_confirmation=True,
        )
