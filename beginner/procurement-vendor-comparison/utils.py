"""Logging, loading, report rendering."""
import json, datetime
def log(msg):
    line = f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S} [INFO] {msg}"
    print(line)
    try:
        with open("log.txt","a") as f: f.write(line+"\n")
    except Exception: pass
def load_json(path):
    with open(path) as f: return json.load(f)
def render_report(req, scores, winner, rationale):
    rows = "\n".join(
        f"| {s.vendor.name} | ₹{s.vendor.unit_price:,.0f} | ₹{s.total_cost:,.0f} | {s.spec_score} | {s.price_score} | {s.risk_score} | {s.delivery_score} | **{s.total_score}** |"
        for s in sorted(scores, key=lambda x: -x.total_score))
    risks = "\n".join(f"- **{s.vendor.name}**: {', '.join(s.risks) or 'No major risks'}" for s in scores)
    return f"""# Vendor Comparison Report
**Request:** {req.raw_text}
**Budget:** ₹{req.budget:,.0f} | **Quantity:** {req.quantity} | **Specs:** {req.specs} | **Delivery ≤ {req.max_delivery_days}d** | **Warranty ≥ {req.min_warranty_years}y**

| Vendor | Unit Price | Total Cost | Spec | Price | Risk | Delivery | Total |
|---|---|---|---|---|---|---|---|
{rows}

## Recommendation: {winner.vendor.name}
{rationale}

## Risks
{risks}
"""
