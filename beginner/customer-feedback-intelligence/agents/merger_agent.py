"""Merger Agent."""
def run(sentiment, product, service, trend, total):
    neg = sentiment["distribution"].get("negative", 0)
    pos = sentiment["distribution"].get("positive", 0)
    lines = []
    lines.append("# Customer Feedback Intelligence Report\n")
    lines.append(f"**Total reviews analysed:** {total}")
    lines.append(f"**Sentiment:** {pos} positive | {neg} negative | {sentiment['distribution'].get('neutral', 0)} neutral")
    lines.append(f"**Satisfaction proxy:** {round(pos/total*100, 1) if total else 0}% positive\n")
    lines.append("## Top Product Issues")
    for i in product["issues"][:5]:
        lines.append(f"- **{i['issue']}** - {i['count']} mentions - e.g. \"{i['example']}\"")
    lines.append("\n## Top Service Issues")
    for i in service["issues"][:5]:
        lines.append(f"- **{i['issue']}** - {i['count']} mentions - e.g. \"{i['example']}\"")
    lines.append("\n## Recurring Trends")
    for t in trend["trends"][:8]:
        lines.append(f"- {t['keyword']} ({t['mentions']} mentions)")
    lines.append("\n## Prioritized Actions")
    actions = []
    if product["issues"]:
        actions.append((f"P0 - Fix top product issue: {product['issues'][0]['issue']}", "Product / QA"))
    if service["issues"]:
        actions.append((f"P0 - Fix top service issue: {service['issues'][0]['issue']}", "Ops / Support"))
    if neg > total * 0.3:
        actions.append(("P1 - Proactive outreach to negative reviewers with refund / replacement offer", "CX"))
    actions.append(("P2 - Double down on what works: highlight top positive themes in marketing", "Marketing"))
    for a, owner in actions:
        lines.append(f"- {a} - Owner: {owner}")
    return "\n".join(lines)
