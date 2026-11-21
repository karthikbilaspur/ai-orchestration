from research_assistant.agents import ResearchAgents
from research_assistant.config import Settings
from research_assistant.models import (
    Analysis, EvidencePoint, ResearchBundle, ResearchRequest, Source
)


class DummyLLM:
    pass


def make_agents():
    return ResearchAgents(
        Settings(openai_api_key="fake"),
        llm=DummyLLM(),
        researcher=object(),
    )


def test_fact_checker_approves_known_citations():
    agents = make_agents()
    state = {
        "request": ResearchRequest(question="Why do cities plant trees?"),
        "research": ResearchBundle(
            question="Why do cities plant trees?",
            sources=[Source(source_id="S1", title="Source", url="https://example.com")],
        ),
        "analysis": Analysis(
            overview="Overview",
            key_findings=[EvidencePoint(claim="Trees provide shade.", source_ids=["S1"])],
        ),
    }
    result = agents.fact_checker_node(state)["fact_check"]
    assert result.approved is True
    assert result.checked_claims == 1


def test_fact_checker_flags_missing_and_unknown_citations():
    agents = make_agents()
    state = {
        "request": ResearchRequest(question="Why do cities plant trees?"),
        "research": ResearchBundle(
            question="Why do cities plant trees?",
            sources=[Source(source_id="S1", title="Source", url="https://example.com")],
        ),
        "analysis": Analysis(
            overview="Overview",
            key_findings=[
                EvidencePoint(claim="Uncited claim."),
                EvidencePoint(claim="Unknown citation.", source_ids=["S99"]),
            ],
        ),
    }
    result = agents.fact_checker_node(state)["fact_check"]
    assert result.approved is False
    assert len(result.issues) == 2
