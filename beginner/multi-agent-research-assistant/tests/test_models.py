import pytest
from pydantic import ValidationError
from research_assistant.models import ResearchRequest, Source


def test_research_request_accepts_valid_depth():
    request = ResearchRequest(question="How do urban trees reduce heat?", depth="deep")
    assert request.depth == "deep"


def test_research_request_rejects_invalid_depth():
    with pytest.raises(ValidationError):
        ResearchRequest(question="How do urban trees reduce heat?", depth="massive")


def test_source_requires_core_fields():
    source = Source(source_id="S1", title="Example", url="https://example.com")
    assert source.source_id == "S1"
