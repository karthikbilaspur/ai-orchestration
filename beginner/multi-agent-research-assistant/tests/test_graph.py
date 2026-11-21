from research_assistant.graph import create_graph
from research_assistant.models import (
    Analysis, EvidencePoint, FactCheckResult, ResearchBundle, ResearchRequest, Source
)


class FakeAgents:
    def researcher_node(self, state):
        return {"research": ResearchBundle(
            question=state["request"].question,
            sources=[Source(source_id="S1", title="Test", url="https://example.com", snippet="Evidence")],
        )}

    def analyst_node(self, state):
        return {"analysis": Analysis(
            overview="Test overview",
            key_findings=[EvidencePoint(claim="Test finding", source_ids=["S1"])],
        )}

    def fact_checker_node(self, state):
        return {"fact_check": FactCheckResult(approved=True, checked_claims=1)}

    def writer_node(self, state):
        assert state["fact_check"].approved
        return {"report_markdown": "# Test report\n\nDone."}


def test_graph_runs_nodes_in_order_and_returns_report():
    app = create_graph(FakeAgents())
    result = app.invoke({"request": ResearchRequest(question="What makes a good test?")})
    assert result["report_markdown"] == "# Test report\n\nDone."
    assert result["research"].sources[0].source_id == "S1"
