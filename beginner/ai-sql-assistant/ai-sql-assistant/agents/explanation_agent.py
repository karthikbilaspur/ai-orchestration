"""Agent 5: Explanation Agent - rows -> plain English."""
def explain(question: str, sql: str, result: dict) -> str:
    rows = result["rows"]
    if not rows:
        return "No results found for your question."
    cols = result["columns"]
    lines = [f"Found {len(rows)} result(s) for: \"{question}\""]
    # Human summary for common shapes
    if "product" in cols and "total_sold" in cols:
        for i, r in enumerate(rows, 1):
            lines.append(f"{i}. {r['product']} — {r['total_sold']} sold, revenue ₹{r.get('revenue', 0):,.0f}")
        lines.append(f"\nTop seller: {rows[0]['product']} with {rows[0]['total_sold']} units sold.")
    elif "category" in cols and "revenue" in cols:
        for r in rows:
            lines.append(f"- {r['category']}: ₹{r['revenue']:,.0f} revenue ({r.get('units',0)} units)")
    elif "total_spent" in cols:
        for i, r in enumerate(rows, 1):
            lines.append(f"{i}. {r['name']} ({r.get('city','')}) — spent ₹{r['total_spent']:,.0f}")
    elif "total_revenue" in cols:
        lines.append(f"Total revenue: ₹{rows[0]['total_revenue']:,.0f} across {rows[0]['order_count']} orders.")
    else:
        for r in rows:
            lines.append(" | ".join(f"{k}: {v}" for k, v in r.items()))
    return "\n".join(lines)
