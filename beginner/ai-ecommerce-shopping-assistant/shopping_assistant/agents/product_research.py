"""Agent 2 - Product Research.

Searches the local catalog: applies the hard filters (category, brand,
budget, minimum specs), scores how relevant each survivor is to the shopper's
stated needs and returns a short list.
"""
from __future__ import annotations

from typing import List

from ..catalog import CATEGORY_SPECS, Catalog
from ..config import BUDGET_RELAX_FACTOR, MAX_SHORTLIST, money
from ..models import Candidate, Product, Requirements, ResearchResult
from .base import BaseAgent


class ProductResearchAgent(BaseAgent):
    name = "ProductResearch"

    def __init__(self, max_results: int = MAX_SHORTLIST, logger=None):
        super().__init__(logger)
        self.max_results = max_results

    def run(self, requirements: Requirements, catalog: Catalog) -> ResearchResult:
        if not requirements.category:
            raise ValueError("Product Research needs a category")

        result = ResearchResult()
        pool: List[Product] = catalog.by_category(requirements.category)
        result.considered = len(pool)
        self.log.info("Category '%s' has %d product(s)", requirements.category, len(pool))

        # 1. brand filter (soft: ignored if it would leave nothing)
        if requirements.brands and pool:
            wanted = {b.lower() for b in requirements.brands}
            branded = [p for p in pool if p.brand.lower() in wanted]
            if branded:
                pool = branded
                result.notes.append("Limited to brand(s): " + ", ".join(requirements.brands))
            else:
                result.notes.append("No products from the requested brand(s); brand filter ignored.")

        # 2. minimum specs (hard). Specs that do not exist for this category are ignored.
        valid_keys = {m.key for m in CATEGORY_SPECS.get(requirements.category, [])}
        for key, minimum in requirements.min_specs.items():
            if key not in valid_keys:
                result.notes.append(f"Ignored requirement '{key} >= {minimum:g}' (not applicable to this category).")
                continue
            pool = [p for p in pool if p.specs.get(key, 0) >= minimum]
            result.notes.append(f"Required {key} >= {minimum:g}.")

        # 3. budget (hard, but we stretch it once before giving up)
        pool = self._apply_budget(pool, requirements, result)

        # 4. relevance to the shopper's needs
        candidates = [self._score(p, requirements) for p in pool]
        if any(c.relevance > 0 for c in candidates) and requirements.tags:
            dropped = [c for c in candidates if c.relevance == 0]
            if dropped:
                result.notes.append(f"Dropped {len(dropped)} product(s) matching none of your needs.")
            candidates = [c for c in candidates if c.relevance > 0]
        candidates.sort(key=lambda c: (-c.relevance, -c.product.rating, c.product.price))
        result.candidates = candidates[: self.max_results]

        self.log.info("Shortlist: %s", [c.product.name for c in result.candidates])
        return result

    # ------------------------------------------------------------- helpers --
    def _apply_budget(self, pool: List[Product], req: Requirements, result: ResearchResult) -> List[Product]:
        low, high = req.min_budget, req.max_budget
        if low is None and high is None:
            return pool

        def within(p: Product, hi: float | None) -> bool:
            return (low is None or p.price >= low) and (hi is None or p.price <= hi)

        filtered = [p for p in pool if within(p, high)]
        if filtered or high is None or not pool:
            return filtered
        stretched = high * BUDGET_RELAX_FACTOR
        filtered = [p for p in pool if within(p, stretched)]
        if filtered:
            result.relaxed_budget = True
            result.notes.append(
                f"Nothing under {money(high)}; stretched the budget by "
                f"{(BUDGET_RELAX_FACTOR - 1):.0%} (to {money(stretched)}).")
        else:
            result.notes.append(f"Nothing found within {money(high)} (or {money(stretched)} with a 20% stretch).")
        return filtered

    @staticmethod
    def _score(product: Product, req: Requirements) -> Candidate:
        if not req.tags:
            return Candidate(product, relevance=0.5)
        matched = tuple(t for t in req.tags if t in product.tags)
        missing = tuple(t for t in req.tags if t not in product.tags)
        return Candidate(product, relevance=len(matched) / len(req.tags),
                         matched_tags=matched, missing_tags=missing)
