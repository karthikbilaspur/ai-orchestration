"""Agent 2: Researcher — gathers info from predefined documents."""
import os, re
from src.core.models import Claim
class ResearcherAgent:
    def __init__(self, docs_dir="data/documents"):
        self.docs_dir = docs_dir
        self.docs = self._load()
    def _load(self):
        docs=[]
        if not os.path.exists(self.docs_dir): return docs
        for fn in sorted(os.listdir(self.docs_dir)):
            if fn.endswith(".md"):
                with open(os.path.join(self.docs_dir, fn), encoding="utf-8") as f:
                    docs.append((fn, f.read()))
        return docs
    def _score(self, text, query):
        qwords = set(re.findall(r"[a-z]+", query.lower()))
        t = text.lower()
        return sum(t.count(w) for w in qwords if len(w)>3)
    def research(self, question, subtopics, max_per_subtopic=5):
        claims=[]
        for sub in subtopics:
            # Rank paragraphs by keyword overlap with subtopic + question
            candidates=[]
            for fn, content in self.docs:
                # Split into sentences / paragraphs
                parts = re.split(r"\n\s*\n|\.\s+", content)
                for p in parts:
                    p=p.strip().replace("\n"," ")
                    if len(p)<40: continue
                    score = self._score(p, sub) + 0.5*self._score(p, question)
                    if score>0:
                        candidates.append((score, fn, p))
            candidates.sort(reverse=True)
            seen=set()
            for score, fn, p in candidates[:max_per_subtopic]:
                if p in seen: continue
                seen.add(p)
                # Claim = first sentence-ish, truncated
                claims.append(Claim(text=p[:220], source=fn, evidence=p[:300], confidence=0.0))
        # Fallback if no docs matched
        if not claims:
            claims.append(Claim(text=f"No direct evidence found in local documents for: {question}",
                                source="none", evidence="No matching document paragraph.", verdict="UNSUPPORTED", confidence=0.0))
        return claims
