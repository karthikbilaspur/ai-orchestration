from agents import sentiment_agent, product_agent, service_agent, trend_agent
from agents.merger_agent import run as merge

REVIEWS = [
    {"id": 1, "text": "I love this, excellent quality and fast delivery"},
    {"id": 2, "text": "Terrible, broken product and rude support, refund please"},
    {"id": 3, "text": "It is okay, nothing special"},
]

def test_sentiment_classifies_all_three():
    out = sentiment_agent.run(REVIEWS)
    assert out["distribution"] == {"positive": 1, "negative": 1, "neutral": 1}

def test_product_and_service_find_issues():
    assert any(i["issue"] == "broken / damaged" for i in product_agent.run(REVIEWS)["issues"])
    assert any(i["issue"] == "refund issue" for i in service_agent.run(REVIEWS)["issues"])

def test_merger_produces_report_with_actions():
    report = merge(sentiment_agent.run(REVIEWS), product_agent.run(REVIEWS), service_agent.run(REVIEWS), trend_agent.run(REVIEWS), 3)
    assert "Customer Feedback" in report and "Prioritized Actions" in report and "P0" in report
