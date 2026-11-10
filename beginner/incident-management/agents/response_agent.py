"""Agent 4: Response Agent - recommends actions by severity + route."""
class ResponseAgent:
    def recommend(self, incident) -> list:
        sev = incident.severity
        base = []
        if sev == "low":
            base = ["Log incident and monitor", "Create low-priority ticket", "Review in next standup - no immediate action"]
        elif sev == "medium":
            base = ["Assign on-call engineer", "Check dashboards / logs for affected service", "Check recent deploys and roll back if suspect", "Add monitoring / alert threshold if missing"]
        elif sev == "critical":
            base = ["PAGE on-call immediately + escalate to incident commander", "Open incident channel / bridge", "Consider rollback / failover / traffic shift", "Freeze deploys for affected service", "Prepare customer status-page update"]
        # Error-specific playbook
        extra = {
            "TimeoutError": ["Increase timeout / circuit breaker check", "Scale up affected service"],
            "ConnectionError": ["Verify service health + restart if needed", "Check LB / service discovery"],
            "OutOfMemoryError": ["Restart affected pods", "Roll back last deploy", "Increase memory limit temporarily"],
            "DiskFull": ["Clear old logs / temp files", "Expand disk / add retention policy"],
            "AuthFailure": ["Verify secrets / cert expiry", "Check IdP status"],
            "RateLimit": ["Enable rate-limit / WAF rule", "Scale or add caching"],
        }.get(incident.error_type, [])
        return base + extra
