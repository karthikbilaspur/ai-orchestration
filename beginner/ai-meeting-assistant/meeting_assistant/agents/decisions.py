"""Decision Extractor agent: finds sentences that record a decision."""
from __future__ import annotations

import logging
import re

from meeting_assistant.parser import DECISION_LABELS, ensure_sentences

log = logging.getLogger(__name__)

MARKER_RE = re.compile(
    r"\b(decided|decision|agreed|approved?|approves|will proceed|going with|go with|finali[sz]ed|"
    r"signed off|resolved to|settled on|let'?s (?:go|proceed|move forward))\b", re.I)
NEGATED_RE = re.compile(
    r"(?:\b(?:not|never|yet to|still need to|need to|haven'?t|hasn'?t|didn'?t|no one|nobody)(?:\s+has|\s+have)?\b|n't)\s+"
    r"(?:\w+\s+){0,2}(?:decide[d]?|agree[d]?|approve[d]?|finali[sz]e[d]?)\b", re.I)
MIN_WORDS = 3


class DecisionExtractorAgent:
    def extract(self, transcript) -> list:
        """Return ``[{"text", "speaker", "timestamp"}, ...]`` in transcript order."""
        found, seen = [], set()
        for s in ensure_sentences(transcript):
            text = s["text"]
            labelled = s["label"] in DECISION_LABELS
            if not labelled:
                if text.endswith("?") or len(text.split()) < MIN_WORDS or text.lower().startswith("if "):
                    continue
                if not MARKER_RE.search(text) or NEGATED_RE.search(text):
                    continue
            key = text.lower()
            if key in seen:
                continue
            seen.add(key)
            found.append({"text": text, "speaker": s["speaker"], "timestamp": s["timestamp"]})
        log.info("Extracted %d decision(s)", len(found))
        return found
