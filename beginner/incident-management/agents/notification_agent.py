"""Agent 5: Notification Agent - prepares incident notification."""
class NotificationAgent:
    def prepare(self, incident) -> str:
        emoji = {"low": "🟢", "medium": "🟡", "critical": "🔴"}.get(incident.severity, "⚪")
        lines = [
            f"{emoji} [{incident.severity.upper()}] {incident.id} - {incident.service} | {incident.error_type}",
            f"Time: {incident.timestamp}",
            f"Route: {incident.route}",
            f"Alert: {incident.message}",
            "",
            "Possible causes:",
        ]
        for c in incident.possible_causes: lines.append(f"  - {c}")
        lines.append("")
        lines.append("Recommended actions:")
        for a in incident.recommended_actions: lines.append(f"  - {a}")
        if incident.severity == "critical":
            lines.append("")
            lines.append("⚠️  ACTION REQUIRED: Page on-call now. Do not wait.")
        return "\n".join(lines)
