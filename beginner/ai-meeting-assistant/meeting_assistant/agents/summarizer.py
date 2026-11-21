"""Summarizer agent: extractive summary and key-topic detection."""
from __future__ import annotations

import logging
import math
import re
from collections import Counter

from meeting_assistant.parser import ensure_sentences

log = logging.getLogger(__name__)

STOPWORDS = set("""
the and but then for with from this that these those its you our your their they them she him her his
not yes okay just also very can could would should will shall may might must have has had does did done
get got going let lets about into over after before again there here what which who whom when where why
how than too out off any all some more most other such only own same few each both thanks thank hello
good morning everyone really like one two are was were been being per via
""".split())

_MARKER_RE = re.compile(r"\b(decided|agreed|approved|will|action|deadline|due|priority|blocker)\b", re.I)
SHORT_SENTENCES, DETAILED_SENTENCES = 3, 8


def tokens(text: str) -> list:
    return [t for t in re.findall(r"[a-z][a-z'-]{2,}", text.lower()) if t not in STOPWORDS]


def _end(text: str) -> str:
    return text if text[-1:] in ".!?" else text + "."


class SummarizerAgent:
    def key_topics(self, transcript, n: int = 5) -> list:
        counts = Counter(t for s in ensure_sentences(transcript) for t in tokens(s["text"]))
        ranked = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
        return [word for word, c in ranked[:n] if c >= 2] or [word for word, _ in ranked[:n]]

    def select(self, transcript, detail: str = "short") -> list:
        sentences = ensure_sentences(transcript)
        cands = [s for s in sentences if len(tokens(s["text"])) >= 2]
        if not cands:
            cands = [s for s in sentences if tokens(s["text"])]
        if not cands:
            return []
        limit = SHORT_SENTENCES if detail == "short" else DETAILED_SENTENCES
        k = min(limit, max(1, math.ceil(len(cands) * 0.6)), len(cands))
        freq = Counter(t for s in cands for t in set(tokens(s["text"])))
        raw = []
        for s in cands:
            toks = set(tokens(s["text"]))
            raw.append(sum(freq[t] for t in toks) / math.sqrt(len(toks) or 1))
        top = max(raw) or 1.0
        scored = []
        for pos, (s, r) in enumerate(zip(cands, raw)):
            bonus = (0.25 if s["label"] or _MARKER_RE.search(s["text"]) else 0) + (0.1 if pos == 0 else 0)
            scored.append((-(r / top + bonus), s["index"], s))
        chosen = sorted(scored)[:k]
        return [s for _, _, s in sorted(chosen, key=lambda t: t[1])]

    def summarize(self, transcript, detail: str = "short") -> str:
        picked = self.select(transcript, detail)
        if not picked:
            return "No transcript content supplied."
        if detail == "short":
            return " ".join(_end(s["text"]) for s in picked)
        return "\n".join(f"- {s['speaker'] + ': ' if s['speaker'] else ''}{_end(s['text'])}" for s in picked)
