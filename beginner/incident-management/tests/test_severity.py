from agents.alert_analyzer import AlertAnalyzer
from agents.severity_agent import SeverityAgent
def test_critical_high_error_rate():
    inc = AlertAnalyzer().analyze("payment timeout 35% error rate")
    assert SeverityAgent().classify(inc) == "critical"
def test_medium_timeout():
    inc = AlertAnalyzer().analyze("api-gateway timeout")
    assert SeverityAgent().classify(inc) == "medium"
def test_low_minor():
    inc = AlertAnalyzer().analyze("frontend minor CSS warning")
    assert SeverityAgent().classify(inc) == "low"
def test_routing():
    s = SeverityAgent()
    assert (s.route("low"), s.route("medium"), s.route("critical")) == ("Log", "Investigate", "Escalate")
