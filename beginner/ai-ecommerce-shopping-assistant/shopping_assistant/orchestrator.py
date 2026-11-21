"""The orchestrator: runs the four agents in order and hands data along.

    query --> RequirementCollector --> ProductResearch --> Comparison --> Recommendation

It has no `buy`, `checkout` or `pay` method - by design the assistant can only
*recommend*.
"""
from __future__ import annotations

import logging
import time
from typing import Optional

from .agents import (ComparisonAgent, ProductResearchAgent,
                     RecommendationAgent, RequirementCollectorAgent)
from .agents.requirement_collector import InputFn
from .catalog import Catalog, load_default_catalog
from .formatting import render_report
from .models import SessionResult

log = logging.getLogger("shopping_assistant.orchestrator")


class ShoppingAssistant:
    def __init__(self, catalog: Optional[Catalog] = None):
        self.catalog = catalog or load_default_catalog()
        self.collector = RequirementCollectorAgent(known_brands=self.catalog.brands())
        self.researcher = ProductResearchAgent()
        self.comparer = ComparisonAgent()
        self.recommender = RecommendationAgent()

    def run(self, query: str, input_fn: Optional[InputFn] = None) -> SessionResult:
        """Run the whole pipeline for one shopper request."""
        result = SessionResult(query=query)
        log.info("=== New request: %r ===", query)

        # 1. Requirement Collector
        started = time.perf_counter()
        result.requirements = self.collector.run(query, input_fn=input_fn)
        self._step(result, "RequirementCollector", result.requirements.summary(), started)
        if result.requirements.missing_fields():
            result.error = ("I could not tell what kind of product you want. "
                            "Try e.g. 'a laptop under 1000 for coding'.")
            log.warning(result.error)
            return result

        # 2. Product Research
        started = time.perf_counter()
        result.research = self.researcher.run(result.requirements, self.catalog)
        self._step(result, "ProductResearch",
                   f"{len(result.research.candidates)} of {result.research.considered} products shortlisted", started)
        if not result.research.candidates:
            result.error = ("No products in the sample catalog match your request. "
                            "Try a higher budget or fewer requirements.")
            log.warning(result.error)
            return result

        # 3. Comparison
        started = time.perf_counter()
        result.comparison = self.comparer.run(result.research)
        self._step(result, "Comparison",
                   f"compared {len(result.comparison.products)} products on {len(result.comparison.rows)} features", started)

        # 4. Recommendation
        started = time.perf_counter()
        result.recommendation = self.recommender.run(result.requirements, result.comparison, result.research)
        self._step(result, "Recommendation", f"top pick: {result.recommendation.best.product.name}", started)
        return result

    def report(self, result: SessionResult) -> str:
        return render_report(result)

    @staticmethod
    def _step(result: SessionResult, agent: str, summary: str, started: float) -> None:
        elapsed_ms = (time.perf_counter() - started) * 1000
        line = f"{agent}: {summary}"
        result.steps.append(line)
        log.info("%s (%.1f ms)", line, elapsed_ms)
