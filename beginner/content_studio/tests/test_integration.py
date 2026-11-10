"""End-to-end: CLI + orchestrator + markdown export."""
from src.main import main
from src.models import TopicRequest
from src.orchestrator import Orchestrator

def test_end_to_end_markdown(tmp_path):
    out = tmp_path / "out.md"
    final = main(["--topic","Rooftop gardening","--audience","beginners","--threshold","50","--output",str(out)])
    assert out.exists() and "Rooftop" in out.read_text()
    assert "Quality Score" in out.read_text()

def test_final_content_to_markdown():
    final = Orchestrator().run(TopicRequest(topic="AI agents", threshold=50), verbose=False)
    md = final.to_markdown()
    assert md.startswith("#") and "SEO" in md and "Review Notes" in md
