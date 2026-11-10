from typing import Optional
"""Agent 1: Query Understanding - NL -> structured intent."""
import re
from dataclasses import dataclass, field

@dataclass
class Intent:
    question: str
    intent_type: str = "general"  # top_products, revenue_by_category, top_customers, list_products, total_revenue, orders_by_city
    limit: int = 5
    min_amount: Optional[float] = None
    category: Optional[str] = None
    sort_desc: bool = True

TOP_PATTERNS = [
    (r"top\s+(\d+).*highest.*sell|top\s+(\d+).*best.*sell|best.*sell", "top_products"),
    (r"revenue.*categor|sales.*categor", "revenue_by_category"),
    (r"top.*customer|customers.*spent|highest.*spend", "top_customers"),
    (r"total.*revenue|total.*sales", "total_revenue"),
    (r"list.*product|show.*product|all.*product", "list_products"),
    (r"orders.*city|sales.*city", "orders_by_city"),
]

def parse_question(question: str) -> Intent:
    q = question.strip()
    low = q.lower()
    intent_type = "general"
    for pat, typ in TOP_PATTERNS:
        if re.search(pat, low):
            intent_type = typ
            break
    m = re.search(r"top\s+(\d+)", low)
    limit = int(m.group(1)) if m else 5
    m2 = re.search(r"(more than|over|above|greater than)\s*(?:rs\.?|\$|inr)?\s*(\d+(?:\.\d+)?)", low)
    min_amount = float(m2.group(2)) if m2 else None
    cat = None
    for c in ["electronics", "apparel", "home"]:
        if c in low:
            cat = c.capitalize()
    # Fallback: if asks top products without explicit type
    if intent_type == "general" and "product" in low:
        intent_type = "top_products"
    return Intent(question=q, intent_type=intent_type, limit=limit, min_amount=min_amount, category=cat)
