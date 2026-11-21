from collections.abc import Callable
from .models import Source, ResearchBundle


class TavilyResearcher:
    \"\"\"Search adapter. Tavily is optional; tests can inject a fake search callable.\"\"\"

    def __init__(
        self,
        api_key: str | None = None,
        max_results: int = 5,
        search_fn: Callable | None = None,
    ):
        self.api_key = api_key
        self.max_results = max_results
        self.search_fn = search_fn

    def search(self, query: str) -> list[Source]:
        if self.search_fn:
            raw_results = self.search_fn(query)
        else:
            if not self.api_key:
                raise RuntimeError(
                    "Web search is not configured. Add TAVILY_API_KEY or provide source text."
                )
            from tavily import TavilyClient
            raw_results = TavilyClient(api_key=self.api_key).search(
                query=query,
                max_results=self.max_results,
                search_depth="basic",
            ).get("results", [])

        sources: list[Source] = []
        for index, item in enumerate(raw_results[: self.max_results], start=1):
            url = str(item.get("url", "")).strip()
            title = str(item.get("title", "Untitled source")).strip()
            snippet = str(item.get("content", item.get("snippet", ""))).strip()
            if not url:
                continue
            sources.append(
                Source(source_id=f"S{index}", title=title, url=url, snippet=snippet)
            )
        return sources


def bundle_from_user_text(question: str, source_text: str) -> ResearchBundle:
    cleaned = source_text.strip()
    if not cleaned:
        raise ValueError("Source text cannot be empty.")
    return ResearchBundle(
        question=question,
        sources=[
            Source(
                source_id="S1",
                title="User-provided source material",
                url="user-provided://source-material",
                snippet=cleaned,
            )
        ],
        research_notes="The source material was supplied by the user; no web search was performed.",
    )
