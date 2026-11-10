"""Trend Agent."""
import re
from collections import Counter
STOP = set("the a an and or of to in is it was for on with my i this that very really just so".split())
def run(reviews):
    c = Counter()
    for r in reviews:
        words = [w for w in re.findall(r"[a-z]{4,}", r["text"].lower()) if w not in STOP]
        c.update(set(words))
    return {"agent": "trend", "trends": [{"keyword": k, "mentions": v} for k, v in c.most_common(10)]}
