"""Entry point - demo + interactive mode."""
from orchestrator import Orchestrator
DEMO_ALERTS = [
    "INFO: frontend - minor CSS warning on homepage",
    "ERROR: auth-service 401 unauthorized - invalid token spike",
    "ERROR: payment-service timeout - 35% error rate, latency 6200ms",
    "CRITICAL: database disk full - no space left, writes failing",
]
def demo():
    orch = Orchestrator()
    for a in DEMO_ALERTS:
        inc = orch.handle_alert(a)
        print(inc.notification); print()
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        orch = Orchestrator()
        print(orch.handle_alert(" ".join(sys.argv[1:])).notification)
    else:
        demo()
