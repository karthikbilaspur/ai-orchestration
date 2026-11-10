from agents.alert_analyzer import AlertAnalyzer
def test_detects_payment_timeout():
    inc = AlertAnalyzer().analyze("payment-service timeout 35% error rate")
    assert inc.service == "payment-service"
    assert inc.error_type == "TimeoutError"
    assert inc.metadata["error_rate_pct"] == 35.0
def test_detects_database():
    inc = AlertAnalyzer().analyze("database connection refused")
    assert inc.service == "database"
def test_unknown_defaults():
    inc = AlertAnalyzer().analyze("something weird happened")
    assert inc.service == "unknown" and inc.error_type == "UnknownError"
