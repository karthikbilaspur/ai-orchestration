from orchestrator import Orchestrator
def test_end_to_end_critical():
    inc = Orchestrator().handle_alert("CRITICAL: database disk full - writes failing")
    assert inc.severity == "critical" and inc.route == "Escalate"
    assert inc.possible_causes and inc.recommended_actions
    assert "PAGE on-call" in inc.notification or "Page on-call" in inc.notification or "PAGE" in inc.notification
def test_end_to_end_low():
    inc = Orchestrator().handle_alert("INFO: frontend minor warning")
    assert inc.severity == "low" and inc.route == "Log"
    assert inc.notification.startswith("🟢")
def test_events_emitted():
    orch = Orchestrator()
    orch.handle_alert("auth-service 401 unauthorized")
    types = [e["event"] for e in orch.events]
    assert "alert_received" in types and "severity_classified" in types and "notification_prepared" in types
