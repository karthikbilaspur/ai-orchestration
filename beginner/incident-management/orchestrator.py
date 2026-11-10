"""Orchestration: System Alert -> Analyzer -> Severity -> Route -> Response -> Notification.
Event-driven: each step emits an event dict to logger / event bus."""
import json, os
from agents.alert_analyzer import AlertAnalyzer
from agents.severity_agent import SeverityAgent
from agents.root_cause_agent import RootCauseAgent
from agents.response_agent import ResponseAgent
from agents.notification_agent import NotificationAgent

LOG_FILE = os.path.join(os.path.dirname(__file__), "logs", "incidents.log")
EVENTS_FILE = os.path.join(os.path.dirname(__file__), "logs", "events.jsonl")

class Orchestrator:
    def __init__(self):
        self.analyzer = AlertAnalyzer()
        self.severity_agent = SeverityAgent()
        self.root_cause = RootCauseAgent()
        self.response = ResponseAgent()
        self.notifier = NotificationAgent()
        self.events = []
    def emit(self, event_type, incident, extra=None):
        ev = {"event": event_type, "incident_id": incident.id, "severity": incident.severity,
              "service": incident.service, "route": incident.route, **(extra or {})}
        self.events.append(ev)
        os.makedirs(os.path.dirname(EVENTS_FILE), exist_ok=True)
        with open(EVENTS_FILE, "a", encoding="utf-8") as f: f.write(json.dumps(ev) + "\n")
        return ev
    def handle_alert(self, raw_alert: str, incident_id: str = None):
        incident = self.analyzer.analyze(raw_alert, incident_id)
        self.emit("alert_received", incident)
        incident.severity = self.severity_agent.classify(incident)
        incident.route = self.severity_agent.route(incident.severity)
        self.emit("severity_classified", incident, {"error_type": incident.error_type})
        self.emit(f"routed_to_{incident.route.lower()}", incident)
        incident.possible_causes = self.root_cause.suggest(incident)
        incident.recommended_actions = self.response.recommend(incident)
        self.emit("response_prepared", incident, {"actions_count": len(incident.recommended_actions)})
        incident.notification = self.notifier.prepare(incident)
        self.emit("notification_prepared", incident)
        # Append human-readable log
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n{'='*70}\n{incident.notification}\n")
        return incident

if __name__ == "__main__":
    import sys
    alert = " ".join(sys.argv[1:]) or "ERROR: payment-service timeout - 35% error rate, latency 6200ms"
    orch = Orchestrator()
    inc = orch.handle_alert(alert)
    print(inc.notification)
