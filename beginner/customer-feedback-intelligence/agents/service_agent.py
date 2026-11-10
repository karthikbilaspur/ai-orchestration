"""Service Agent."""
KEYWORDS = {"delivery":"delivery delay","late":"late delivery","support":"support unresponsive","refund":"refund issue","rude":"rude staff","cancel":"cancellation","shipping":"shipping","return":"return process","wait":"long wait","chat":"chat / call support"}
def run(reviews):
    counts, examples = {}, {}
    for r in reviews:
        t = r["text"].lower()
        for kw, label in KEYWORDS.items():
            if kw in t:
                counts[label] = counts.get(label, 0) + 1
                examples.setdefault(label, r["text"][:120])
    ranked = sorted(counts.items(), key=lambda x: -x[1])
    return {"agent": "service", "issues": [{"issue": k, "count": v, "example": examples[k]} for k, v in ranked]}
