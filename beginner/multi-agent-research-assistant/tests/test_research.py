import pytest
from research_assistant.research import TavilyResearcher, bundle_from_user_text


def test_search_maps_results_to_stable_source_ids():
    researcher = TavilyResearcher(
        search_fn=lambda query: [
            {"title": "One", "url": "https://one.test", "content": "Snippet one"},
            {"title": "Two", "url": "https://two.test", "content": "Snippet two"},
        ],
        max_results=3,
    )
    results = researcher.search("test query")
    assert [item.source_id for item in results] == ["S1", "S2"]
    assert results[0].snippet == "Snippet one"


def test_search_skips_items_without_urls():
    researcher = TavilyResearcher(
        search_fn=lambda query: [{"title": "No URL", "content": "Not linkable"}]
    )
    assert researcher.search("query") == []


def test_missing_search_key_fails_clearly():
    with pytest.raises(RuntimeError, match="TAVILY_API_KEY"):
        TavilyResearcher().search("query")


def test_user_source_text_creates_bundle():
    bundle = bundle_from_user_text("Research question", "Evidence supplied by user.")
    assert bundle.sources[0].source_id == "S1"
    assert "no web search" in bundle.research_notes


def test_empty_user_source_text_rejected():
    with pytest.raises(ValueError):
        bundle_from_user_text("Question", "   ")
