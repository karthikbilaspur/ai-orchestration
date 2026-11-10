"""Product Agent."""
KEYWORDS = {"quality":"quality","broken":"broken / damaged","defective":"defective","durability":"durability","packaging":"packaging","battery":"battery","size":"size / fit","color":"color","feature":"missing feature","price":"price / value","material":"material"}
def run(reviews):
    counts, examples = {}, {}
    for r in reviews:
        t = r["text"].lower()
        for kw, label in KEYWORDS.items():
            if kw in t:
                counts[label] = counts.get(label, 0) + 1
                examples.setdefault(label, r["text"][:120])
    ranked = sorted(counts.items(), key=lambda x: -x[1])
    return {"agent": "product", "issues": [{"issue": k, "count": v, "example": examples[k]} for k, v in ranked]}
