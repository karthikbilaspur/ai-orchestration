import pytest
from src.models import TopicRequest, Draft, SEOPlan, Review
from src.agents.research_agent import ResearchAgent
from src.agents.writer_agent import WriterAgent
from src.agents.seo_agent import SEOAgent
from src.agents.critic_agent import CriticAgent
from src.agents.editor_agent import EditorAgent

@pytest.fixture
def req(): return TopicRequest(topic="Rooftop gardening", audience="beginners")

def test_research_returns_brief(req):
    b = ResearchAgent().run(req)
    assert b.topic == req.topic and len(b.key_points) >= 3 and len(b.suggested_outline) >= 3

def test_writer_creates_draft(req):
    b = ResearchAgent().run(req); d = WriterAgent().run(req, b)
    assert d.word_count > 50 and "##" in d.body

def test_writer_short_is_shorter(req):
    req.length="short"; b=ResearchAgent().run(req)
    short=WriterAgent().run(req,b); req.length="medium"; med=WriterAgent().run(req,b)
    assert short.word_count <= med.word_count

def test_seo_plan(req):
    b=ResearchAgent().run(req); d=WriterAgent().run(req,b); s=SEOAgent().run(req,d,b)
    assert s.primary_keyword and s.meta_title and s.meta_description

def test_critic_scores_and_overall():
    r = CriticAgent().run(Draft(title="T", body="## A\n\nHello world. "*30), SEOPlan(primary_keyword="hello"))
    assert 0 <= r.overall <= 100 and isinstance(r.issues, list)

def test_editor_increments_version_and_adds_keyword():
    d=Draft(title="T", body="## The short version\n\nHello.", version=1)
    rev=Review(clarity=60, structure=60, depth=60, seo_fit=60, tone_fit=60, issues=["Primary keyword not found"])
    out=EditorAgent().run(d, rev, SEOPlan(primary_keyword="rooftop gardening"))
    assert out.version==2 and "rooftop gardening" in out.body.lower()
