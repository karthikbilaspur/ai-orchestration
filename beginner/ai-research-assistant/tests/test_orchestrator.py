from src.core.orchestrator import run_research
def test_end_to_end():
    r = run_research("What are the benefits and risks of intermittent fasting?")
    assert r.question and r.claims and 0 <= r.confidence <= 1
    assert r.status in ("PASS","PASS_WITH_WARNING","FAIL")
