"""Agent 3: Root Cause Agent - suggests possible causes."""
CAUSES = {
    "TimeoutError": ["Downstream service slow / unresponsive", "Connection pool exhausted", "Database query missing index / slow query", "Network congestion / DNS issue"],
    "ConnectionError": ["Service crashed / not running", "Wrong host/port or firewall rule", "Load balancer misconfiguration", "Pod / container OOM-killed and restarting"],
    "OutOfMemoryError": ["Memory leak in recent deploy", "Unbounded cache / queue growth", "Traffic spike beyond capacity"],
    "HighLatency": ["Slow DB query", "Cache miss storm / cache eviction", "Noisy neighbour / CPU saturation", "Downstream dependency latency"],
    "HighErrorRate": ["Bad deploy / broken release", "Config change / env var missing", "Dependency outage", "Schema migration failure"],
    "DiskFull": ["Logs not rotated", "Unbounded uploads / temp files", "Database growth without cleanup"],
    "AuthFailure": ["Expired / rotated secret not updated", "Clock skew breaking JWT validation", "Identity provider outage"],
    "RateLimit": ["Traffic spike / bot traffic", "Retry storm from clients", "Rate-limit config too low"],
    "UnknownError": ["Unknown - check logs and recent deploys", "Config drift", "Dependency failure"],
}
class RootCauseAgent:
    def suggest(self, incident) -> list:
        return CAUSES.get(incident.error_type, CAUSES["UnknownError"])
