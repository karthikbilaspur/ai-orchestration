"""Plain data containers that the agents pass to each other.

Every agent receives one of these objects and returns another one. Keeping the
data classes separate from the logic makes the pipeline easy to follow and test.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from .config import money


@dataclass(frozen=True)
class Product:
    """One item in the sample catalog."""

    id: str
    name: str
    category: str
    brand: str
    price: float
    rating: float                      # 0-5 stars
    specs: Dict[str, float]            # numeric specs (booleans stored as 1/0)
    tags: Tuple[str, ...] = ()         # what the product is good for


@dataclass
class Requirements:
    """What the shopper wants - the output of the Requirement Collector."""

    raw_query: str = ""
    category: Optional[str] = None
    max_budget: Optional[float] = None
    min_budget: Optional[float] = None
    tags: List[str] = field(default_factory=list)          # needs, e.g. coding
    brands: List[str] = field(default_factory=list)
    min_specs: Dict[str, float] = field(default_factory=dict)  # e.g. ram_gb >= 16
    priorities: List[str] = field(default_factory=list)    # e.g. battery, light

    def missing_fields(self) -> List[str]:
        """Names of the must-have fields that are still unknown."""
        return ["category"] if not self.category else []

    def summary(self) -> str:
        parts = [f"Category: {self.category.replace('_', ' ') if self.category else '?'}"]
        if self.min_budget is not None and self.max_budget is not None:
            parts.append(f"Budget: {money(self.min_budget)}-{money(self.max_budget)}")
        elif self.max_budget is not None:
            parts.append(f"Budget: up to {money(self.max_budget)}")
        elif self.min_budget is not None:
            parts.append(f"Budget: from {money(self.min_budget)}")
        else:
            parts.append("Budget: not set")
        if self.tags:
            parts.append("Needs: " + ", ".join(self.tags))
        if self.priorities:
            parts.append("Priorities: " + ", ".join(self.priorities))
        if self.brands:
            parts.append("Brands: " + ", ".join(self.brands))
        if self.min_specs:
            parts.append("Min specs: " + ", ".join(f"{k}>={v:g}" for k, v in self.min_specs.items()))
        return " | ".join(parts)


# ---------------------------------------------------------------- research --
@dataclass
class Candidate:
    """A product that survived the filters, plus why it is relevant."""

    product: Product
    relevance: float                       # 0-1, share of requested needs matched
    matched_tags: Tuple[str, ...] = ()
    missing_tags: Tuple[str, ...] = ()


@dataclass
class ResearchResult:
    candidates: List[Candidate] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)
    relaxed_budget: bool = False
    considered: int = 0                    # products looked at in the category


# -------------------------------------------------------------- comparison --
@dataclass
class ComparisonRow:
    key: str
    label: str
    unit: str
    kind: str                              # "num" or "bool"
    higher_is_better: bool
    values: Dict[str, float]               # product id -> value
    best_ids: List[str] = field(default_factory=list)
    worst_ids: List[str] = field(default_factory=list)


@dataclass
class ComparisonTable:
    products: List[Product] = field(default_factory=list)
    rows: List[ComparisonRow] = field(default_factory=list)

    def row(self, key: str) -> Optional[ComparisonRow]:
        for r in self.rows:
            if r.key == key:
                return r
        return None


# ---------------------------------------------------------- recommendation --
@dataclass
class ScoredProduct:
    product: Product
    score: float                           # 0-1
    breakdown: Dict[str, float] = field(default_factory=dict)
    reasons: List[str] = field(default_factory=list)
    tradeoffs: List[str] = field(default_factory=list)


@dataclass
class Recommendation:
    ranked: List[ScoredProduct] = field(default_factory=list)
    explanation: str = ""
    notes: List[str] = field(default_factory=list)
    weights_used: Dict[str, float] = field(default_factory=dict)

    @property
    def best(self) -> Optional[ScoredProduct]:
        return self.ranked[0] if self.ranked else None


# ----------------------------------------------------------------- session --
@dataclass
class SessionResult:
    """Everything produced by one run of the pipeline."""

    query: str
    requirements: Optional[Requirements] = None
    research: Optional[ResearchResult] = None
    comparison: Optional[ComparisonTable] = None
    recommendation: Optional[Recommendation] = None
    error: Optional[str] = None
    steps: List[str] = field(default_factory=list)   # human-readable trace

    @property
    def ok(self) -> bool:
        return self.error is None and self.recommendation is not None
