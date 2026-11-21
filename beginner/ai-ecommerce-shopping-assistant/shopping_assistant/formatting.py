"""Turns the data objects into readable text (used by the CLI, README and log)."""
from __future__ import annotations

from typing import List

from .config import DISCLAIMER, money
from .models import (ComparisonRow, ComparisonTable, Recommendation,
                     Requirements, ResearchResult, SessionResult)


def format_value(key: str, kind: str, unit: str, value: float) -> str:
    """Show one spec value the way a shopper expects to read it."""
    if key == "price":
        return money(value)
    if key == "rating":
        return f"{value:.1f}/5"
    if kind == "bool":
        return "Yes" if value else "No"
    if unit.startswith("/"):
        return f"{value:g}{unit}"
    return f"{value:g} {unit}".strip()


def format_row_value(row: ComparisonRow, value: float) -> str:
    return format_value(row.key, row.kind, row.unit, value)


def render_requirements(req: Requirements) -> str:
    return req.summary()


def render_research(research: ResearchResult) -> str:
    lines: List[str] = [f"Looked at {research.considered} product(s), shortlisted {len(research.candidates)}."]
    for note in research.notes:
        lines.append(f"  note: {note}")
    for c in research.candidates:
        matched = ", ".join(c.matched_tags) if c.matched_tags else "-"
        lines.append(f"  - {c.product.name} ({money(c.product.price)}, {c.product.rating:.1f}/5) "
                     f"relevance {c.relevance:.0%}, matches: {matched}")
    return "\n".join(lines)


def render_comparison(table: ComparisonTable) -> str:
    if not table.products:
        return "(nothing to compare)"
    header = ["Feature"] + [p.name for p in table.products]
    body = []
    for row in table.rows:
        label = row.label
        cells = [label]
        for p in table.products:
            text = format_row_value(row, row.values[p.id])
            if p.id in row.best_ids:
                text += " *"
            cells.append(text)
        body.append(cells)
    widths = [max(len(r[i]) for r in [header] + body) for i in range(len(header))]

    def fmt(cells: List[str]) -> str:
        return " | ".join(c.ljust(widths[i]) for i, c in enumerate(cells))

    lines = [fmt(header), "-+-".join("-" * w for w in widths)]
    lines += [fmt(r) for r in body]
    if any(r.best_ids for r in table.rows):
        lines.append("(* = best value in that row)")
    return "\n".join(lines)


def render_recommendation(rec: Recommendation) -> str:
    if not rec.ranked:
        return "(no recommendation)"
    lines: List[str] = []
    for i, sp in enumerate(rec.ranked, start=1):
        tag = "  <-- TOP PICK" if i == 1 else ""
        lines.append(f"#{i} {sp.product.name} - score {sp.score * 100:.0f}/100 "
                     f"({money(sp.product.price)}){tag}")
        for r in sp.reasons:
            lines.append(f"     + {r}")
        for t in sp.tradeoffs:
            lines.append(f"     - {t}")
        parts = " | ".join(f"{k} {v * 100:.0f}" for k, v in sp.breakdown.items())
        lines.append(f"     score parts: {parts}")
    if rec.explanation:
        lines.append("")
        lines.append("Why the top pick: " + rec.explanation)
    for note in rec.notes:
        lines.append(f"note: {note}")
    return "\n".join(lines)


def render_report(result: SessionResult) -> str:
    out: List[str] = [f'Shopper request: "{result.query}"', ""]
    if result.requirements:
        out += ["=== 1. Requirements (Requirement Collector) ===", render_requirements(result.requirements), ""]
    if result.research:
        out += ["=== 2. Research (Product Research) ===", render_research(result.research), ""]
    if result.comparison:
        out += ["=== 3. Comparison (Comparison agent) ===", render_comparison(result.comparison), ""]
    if result.recommendation:
        out += ["=== 4. Recommendation (Recommendation agent) ===",
                render_recommendation(result.recommendation), ""]
    if result.error:
        out += [f"!! {result.error}", ""]
    out.append(DISCLAIMER)
    return "\n".join(out)
