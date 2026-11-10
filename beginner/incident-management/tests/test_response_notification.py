from agents.alert_analyzer import AlertAnalyzer
from agents.response_agent import ResponseAgent
from agents.root_cause_agent import RootCauseAgent
from agents.notification_agent import NotificationAgent
def test_root_cause_and_response():
    inc = AlertAnalyzer().analyze("redis cache timeout")
    inc.severity = "medium"; inc.route = "Investigate"
    inc.possible_causes = RootCauseAgent().suggest(inc)
    inc.recommended_actions = ResponseAgent().recommend(inc)
    assert len(inc.possible_causes) >= 2 and len(inc.recommended_actions) >= 3
def test_notification_format():
    inc = AlertAnalyzer().analyze("payment timeout 30%")
    inc.severity = "critical"; inc.route = "Escalate"
    inc.possible_causes = ["Downstream slow"]; inc.recommended_actions = ["Page on-call"]
    n = NotificationAgent().prepare(inc)
    assert "CRITICAL" in n and "payment-service" in n and "Page on-call" in n
