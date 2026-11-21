"""Agent 3 - Comparison.

Builds a side-by-side table (price, rating and the category's key specs) and
marks the best and worst product in every row.
"""
from __future__ import annotations

from typing import List

from ..catalog import CATEGORY_SPECS, PRICE_META, RATING_META, SpecMeta
from ..config import COMPARE_TOP_N
from ..models import ComparisonRow, ComparisonTable, Product, ResearchResult
from .base import BaseAgent


class ComparisonAgent(BaseAgent):
    name = "Comparison"

    def __init__(self, top_n: int = COMPARE_TOP_N, logger=None):
        super().__init__(logger)
        self.top_n = top_n

    def run(self, research: ResearchResult) -> ComparisonTable:
        products = [c.product for c in research.candidates[: self.top_n]]
        if not products:
            self.log.info("Nothing to compare")
            return ComparisonTable()

        metas: List[SpecMeta] = [PRICE_META, RATING_META] + list(CATEGORY_SPECS.get(products[0].category, []))
        rows = [self._build_row(meta, products) for meta in metas]
        self.log.info("Compared %d product(s) over %d row(s)", len(products), len(rows))
        return ComparisonTable(products=products, rows=rows)

    @staticmethod
    def _value(product: Product, key: str) -> float:
        if key == "price":
            return product.price
        if key == "rating":
            return product.rating
        return product.specs[key]

    def _build_row(self, meta: SpecMeta, products: List[Product]) -> ComparisonRow:
        values = {p.id: self._value(p, meta.key) for p in products}
        row = ComparisonRow(key=meta.key, label=meta.label, unit=meta.unit, kind=meta.kind,
                            higher_is_better=meta.higher_is_better, values=values)
        lo, hi = min(values.values()), max(values.values())
        if lo != hi:                      # if everyone ties there is no winner
            best_value = hi if meta.higher_is_better else lo
            worst_value = lo if meta.higher_is_better else hi
            row.best_ids = [pid for pid, v in values.items() if v == best_value]
            row.worst_ids = [pid for pid, v in values.items() if v == worst_value]
        return row
