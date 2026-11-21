"""Agent 4 - Recommendation.

Scores every compared product, ranks them and - most importantly - explains
the ranking in plain language (reasons for, trade-offs against).
"""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from ..catalog import get_spec_meta, resolve_priority
from ..config import SCORE_WEIGHTS, money
from ..formatting import format_row_value
from ..models import (Candidate, ComparisonTable, Product, Recommendation,
                      Requirements, ResearchResult, ScoredProduct)
from .base import BaseAgent

_COMPONENT_PHRASES = {
    "fit": "it matches your stated needs better",
    "quality": "it has better customer ratings",
    "value": "it is better value for the price",
    "priority": "it does better on the things you said matter most",
}


def normalize(values: List[float], higher_is_better: bool = True) -> List[float]:
    """Scale numbers to 0-1 (1 = best). If all are equal everyone gets 0.5."""
    lo, hi = min(values), max(values)
    if hi == lo:
        return [0.5] * len(values)
    scaled = [(v - lo) / (hi - lo) for v in values]
    return scaled if higher_is_better else [1 - s for s in scaled]


class RecommendationAgent(BaseAgent):
    name = "Recommendation"

    def __init__(self, weights: Optional[Dict[str, float]] = None, logger=None):
        super().__init__(logger)
        self.weights = dict(weights or SCORE_WEIGHTS)

    def run(self, requirements: Requirements, comparison: ComparisonTable,
            research: ResearchResult) -> Recommendation:
        products = comparison.products
        if not products:
            raise ValueError("Recommendation needs at least one compared product")

        rec = Recommendation()
        candidates: Dict[str, Candidate] = {c.product.id: c for c in research.candidates}

        # --- which spec keys do the shopper's priorities map to? ------------
        priority_keys: List[Tuple[str, str]] = []
        for word in requirements.priorities:
            key = resolve_priority(requirements.category or products[0].category, word)
            if key and comparison.row(key):
                priority_keys.append((word, key))
            else:
                rec.notes.append(f"Ignored priority '{word}' - it does not apply to this category.")

        # --- score components, each 0-1 --------------------------------------
        fit = [candidates[p.id].relevance if p.id in candidates else 0.5 for p in products]
        quality = [p.rating / 5 for p in products]
        cheapest = min(p.price for p in products)
        value = [cheapest / p.price for p in products]      # cheapest = 1.0
        priority = self._priority_scores(products, comparison, priority_keys)

        components: Dict[str, List[float]] = {"fit": fit, "quality": quality, "value": value}
        weights = {k: self.weights[k] for k in components}
        if not requirements.tags:
            weights.pop("fit")          # everyone ties on fit, so it says nothing
            components.pop("fit")
        if priority is not None:
            components["priority"] = priority
            weights["priority"] = self.weights["priority"]
        total_w = sum(weights.values())
        rec.weights_used = {k: round(w / total_w, 3) for k, w in weights.items()}

        # --- build scored products -------------------------------------------
        scored: List[ScoredProduct] = []
        for i, p in enumerate(products):
            parts = {k: components[k][i] for k in components}
            score = sum(weights[k] * parts[k] for k in parts) / total_w
            sp = ScoredProduct(product=p, score=score, breakdown=parts)
            self._explain(sp, requirements, comparison, candidates.get(p.id), priority_keys)
            scored.append(sp)
        scored.sort(key=lambda s: (-s.score, -s.product.rating, s.product.price))
        rec.ranked = scored
        top = scored[0]
        if research.relaxed_budget:
            rec.notes.append("Your budget was stretched to find options, so the picks may cost more than you planned.")
        top_cand = candidates.get(top.product.id)
        if requirements.tags and top_cand and top_cand.relevance == 0:
            rec.notes.append("No product in the catalog matches your stated needs ("
                             + ", ".join(requirements.tags) + "); this is only the closest option.")
        rec.explanation = self._why_top(scored, rec.weights_used)
        self.log.info("Ranking: %s", [(s.product.name, round(s.score, 3)) for s in scored])
        return rec

    # ------------------------------------------------------------- helpers --
    @staticmethod
    def _priority_scores(products: List[Product], comparison: ComparisonTable,
                         priority_keys: List[Tuple[str, str]]) -> Optional[List[float]]:
        if not priority_keys:
            return None
        per_key = []
        for _, key in priority_keys:
            row = comparison.row(key)
            vals = [row.values[p.id] for p in products]
            per_key.append(normalize(vals, higher_is_better=row.higher_is_better))
        return [sum(col) / len(col) for col in zip(*per_key)]

    @staticmethod
    def _explain(sp: ScoredProduct, req: Requirements, comparison: ComparisonTable,
                 cand: Optional[Candidate], priority_keys: List[Tuple[str, str]]) -> None:
        p = sp.product
        many = len(comparison.products) > 1

        if req.tags and cand:
            if cand.matched_tags:
                sp.reasons.append("Matches what you asked for: " + ", ".join(cand.matched_tags))
            if cand.missing_tags:
                sp.tradeoffs.append("Not specifically suited for: " + ", ".join(cand.missing_tags))

        rating_row, price_row = comparison.row("rating"), comparison.row("price")
        if many and rating_row and p.id in rating_row.best_ids:
            sp.reasons.append(f"Highest rated of the shortlist ({p.rating:.1f}/5)")
        elif p.rating >= 4.5:
            sp.reasons.append(f"Excellent reviews ({p.rating:.1f}/5)")
        if many and price_row and p.id in price_row.best_ids:
            sp.reasons.append(f"Lowest price of the shortlist ({money(p.price)})")
        if many and price_row and p.id in price_row.worst_ids:
            sp.tradeoffs.append(f"Most expensive of the shortlist ({money(p.price)})")

        if req.max_budget is not None:
            if p.price <= req.max_budget:
                sp.reasons.append(f"Within your {money(req.max_budget)} budget")
            else:
                sp.tradeoffs.append(f"Over your budget by {money(p.price - req.max_budget)}")

        for word, key in priority_keys:
            row = comparison.row(key)
            if key == "price" or row is None:
                continue                      # price is already covered above
            shown = format_row_value(row, row.values[p.id])
            if p.id in row.best_ids:
                sp.reasons.append(f"Best {row.label.lower()} of the shortlist ({shown}) - you wanted '{word}'")
            elif p.id in row.worst_ids:
                sp.tradeoffs.append(f"Weakest {row.label.lower()} of the shortlist ({shown})")

        if not sp.tradeoffs:
            sp.tradeoffs.append("No major trade-offs compared with the other options")

    @staticmethod
    def _why_top(scored: List[ScoredProduct], weights: Dict[str, float]) -> str:
        top = scored[0]
        if len(scored) == 1:
            return f"{top.product.name} is the only product that fits your request."
        second = scored[1]
        # How many score points each ingredient contributed to the lead.
        diffs = {k: weights.get(k, 0) * (top.breakdown[k] - second.breakdown.get(k, 0))
                 for k in top.breakdown}
        margin = (top.score - second.score) * 100
        winners = [k for k, gap in sorted(diffs.items(), key=lambda kv: -kv[1]) if gap >= 0.02][:2]
        if not winners:
            return (f"{top.product.name} edges out {second.product.name} by {margin:.0f} points; "
                    f"the two are very close, so either is a reasonable choice.")
        because = " and ".join(_COMPONENT_PHRASES[k] for k in winners)
        return f"{top.product.name} beats {second.product.name} by {margin:.0f} points, mainly because {because}."
