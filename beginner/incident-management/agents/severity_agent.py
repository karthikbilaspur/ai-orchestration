"""Agent 2: Severity Agent - low / medium / critical + routing."""
class SeverityAgent:
    CRITICAL_KEYWORDS = ["payment", "database", "out of memory", "disk full", "data loss", "down", "outage"]
    def classify(self, incident) -> str:
        text = (incident.raw_alert + " " + incident.error_type).lower()
        meta = incident.metadata
        # Critical rules
        if meta.get("error_rate_pct", 0) >= 20: return "critical"
        if meta.get("latency_ms", 0) >= 5000: return "critical"
        if any(k in text for k in ["payment", "database", "outage", "down", "data loss", "disk full", "out of memory"]):
            return "critical"
        if incident.error_type in ("TimeoutError", "ConnectionError", "HighErrorRate"):
            return "medium"
        if incident.error_type in ("HighLatency", "RateLimit"):
            return "medium"
        if incident.error_type in ("AuthFailure",):
            return "medium"
        return "low"
    def route(self, severity: str) -> str:
        return {"low": "Log", "medium": "Investigate", "critical": "Escalate"}.get(severity, "Log")
