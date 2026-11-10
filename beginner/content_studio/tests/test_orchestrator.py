from src.models import TopicRequest
from src.orchestrator import Orchestrator

def test_pipeline_passes_threshold():
    final = Orchestrator().run(TopicRequest(topic="Rooftop gardening", threshold=50), verbose=False)
    assert final.review.overall >= 50 and final.draft.word_count > 50

def test_max_loops_respected():
    # Impossible threshold forces max loops
    final = Orchestrator().run(TopicRequest(topic="X", threshold=100, max_loops=2), verbose=False)
    assert final.loops_used <= 2

def test_no_seo_mode():
    final = Orchestrator(use_seo=False).run(TopicRequest(topic="X", threshold=50), verbose=False)
    assert final.seo.primary_keyword == ""
