import logging
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from .config import Settings
from .models import Analysis, FactCheckResult, ResearchBundle, ResearchReport
from .state import ResearchState
from .research import TavilyResearcher, bundle_from_user_text

logger = logging.getLogger(__name__)


def build_llm(settings: Settings):
    if not settings.openai_api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is missing. Copy .env.example to .env and add your key."
        )
    return ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        temperature=0,
    )


class ResearchAgents:
    \"\"\"Four specialist nodes. Dependencies are injected for testability.\"\"\"

    def __init__(self, settings: Settings, llm=None, researcher=None):
        self.settings = settings
        self.llm = llm or build_llm(settings)
        self.researcher = researcher or TavilyResearcher(
            api_key=settings.tavily_api_key,
            max_results=settings.max_search_results,
        )

    def researcher_node(self, state: ResearchState) -> dict:
        request = state["request"]
        if request.source_text:
            bundle = bundle_from_user_text(request.question, request.source_text)
        else:
            sources = self.researcher.search(request.question)
            if not sources:
                raise RuntimeError("Search returned no usable sources.")
            bundle = ResearchBundle(
                question=request.question,
                sources=sources,
                research_notes="Sources retrieved from web search. Snippets are leads, not proof.",
            )
        logger.info("Researcher collected %d source(s)", len(bundle.sources))
        return {"research": bundle}

    def analyst_node(self, state: ResearchState) -> dict:
        research = state["research"]
        prompt = ChatPromptTemplate.from_messages([
            ("system",
             "You are a careful research analyst. Use ONLY the supplied source snippets. "
             "Do not add outside facts. Every key finding must cite one or more source IDs "
             "that appear in the input. State uncertainty and disagreements."),
            ("human",
             "Research question: {question}\nAudience: {audience}\nDepth: {depth}\n"
             "Sources:\n{sources}\nResearch notes: {notes}\n"
             "Return a structured analysis.")
        ])
        chain = prompt | self.llm.with_structured_output(Analysis)
        analysis = chain.invoke({
            "question": research.question,
            "audience": state["request"].audience,
            "depth": state["request"].depth,
            "sources": "\n".join(
                f"[{s.source_id}] {s.title}\nURL: {s.url}\nSnippet: {s.snippet}"
                for s in research.sources
            ),
            "notes": research.research_notes,
        })
        return {"analysis": analysis}

    def fact_checker_node(self, state: ResearchState) -> dict:
        known_ids = {source.source_id for source in state["research"].sources}
        issues: list[str] = []
        claims = state["analysis"].key_findings
        for index, claim in enumerate(claims, start=1):
            if not claim.source_ids:
                issues.append(f"Finding {index} has no source citation.")
            unknown = sorted(set(claim.source_ids) - known_ids)
            if unknown:
                issues.append(
                    f"Finding {index} cites unknown source ID(s): {', '.join(unknown)}."
                )
            if claim.confidence == "high" and claim.caveat:
                # Not an error; this is surfaced for human review.
                issues.append(f"Finding {index} has high confidence but also a caveat; review it.")
        result = FactCheckResult(
            approved=not any("no source citation" in item or "unknown source ID" in item for item in issues),
            issues=issues,
            checked_claims=len(claims),
        )
        return {"fact_check": result}

    def writer_node(self, state: ResearchState) -> dict:
        prompt = ChatPromptTemplate.from_messages([
            ("system",
             "You are a precise research writer. Write a Markdown report for the requested "
             "audience and depth. Do not introduce claims beyond the analysis. Include source "
             "IDs in citations like [S1]. Include a limitations section. If fact-check issues "
             "exist, clearly disclose them. Never invent URLs."),
            ("human",
             "Question: {question}\nAudience: {audience}\nDepth: {depth}\n"
             "Analysis: {analysis}\nFact-check: {fact_check}\nSources: {sources}\n"
             "Write the complete report in Markdown.")
        ])
        response = (prompt | self.llm).invoke({
            "question": state["request"].question,
            "audience": state["request"].audience,
            "depth": state["request"].depth,
            "analysis": state["analysis"].model_dump_json(),
            "fact_check": state["fact_check"].model_dump_json(),
            "sources": "\n".join(
                f"[{s.source_id}] {s.title} — {s.url}"
                for s in state["research"].sources
            ),
        })
        content = response.content
        if not isinstance(content, str):
            content = str(content)
        return {"report_markdown": content}
