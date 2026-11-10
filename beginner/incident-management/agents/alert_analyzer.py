"""Agent 1: Alert Analyzer - parses raw alert into structured incident."""
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone

@dataclass
class Incident:
    id: str
    raw_alert: str
    service: str = "unknown"
    error_type: str = "unknown"
    message: str = ""
    timestamp: str = ""
    metadata: dict = field(default_factory=dict)
    severity: str = "unclassified"
    possible_causes: list = field(default_factory=list)
    recommended_actions: list = field(default_factory=list)
    route: str = ""
    notification: str = ""

class AlertAnalyzer:
    """Understands error/alert text. Rule-based + keyword extraction (no LLM needed)."""
    SERVICE_PATTERNS = {
        "api-gateway": r"api[-_ ]?gateway|gateway",
        "auth-service": r"auth|login|token|jwt|oauth",
        "payment-service": r"payment|checkout|stripe|billing|transaction",
        "database": r"database|db|postgres|mysql|sql|connection pool",
        "cache": r"redis|cache|memcached",
        "frontend": r"frontend|react|ui|web|cdn",
        "worker": r"worker|queue|celery|kafka|job",
    }
    ERROR_PATTERNS = {
        "TimeoutError": r"timeout|timed out|504|deadline exceeded",
        "ConnectionError": r"connection (refused|reset|failed)|econnrefused|unreachable|502|503",
        "OutOfMemoryError": r"out of memory|oom|memory leak|heap",
        "HighLatency": r"latency|slow|p95|p99|response time",
        "HighErrorRate": r"5xx|error rate|500|failures? spike",
        "DiskFull": r"disk full|no space|storage",
        "AuthFailure": r"401|403|unauthorized|invalid token",
        "RateLimit": r"429|rate limit|throttl",
    }
    def analyze(self, raw_alert: str, incident_id: str = None) -> Incident:
        low = raw_alert.lower()
        service = "unknown"
        for name, pat in self.SERVICE_PATTERNS.items():
            if re.search(pat, low):
                service = name; break
        error_type = "UnknownError"
        for name, pat in self.ERROR_PATTERNS.items():
            if re.search(pat, low):
                error_type = name; break
        # Extract numbers like error rate, latency for metadata
        metadata = {}
        m = re.search(r"(\d+(?:\.\d+)?)%", raw_alert)
        if m: metadata["error_rate_pct"] = float(m.group(1))
        m2 = re.search(r"(\d+)\s*ms", raw_alert)
        if m2: metadata["latency_ms"] = int(m2.group(1))
        return Incident(
            id=incident_id or f"INC-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
            raw_alert=raw_alert, service=service, error_type=error_type,
            message=raw_alert.strip()[:300],
            timestamp=datetime.now(timezone.utc).isoformat(),
            metadata=metadata,
        )
