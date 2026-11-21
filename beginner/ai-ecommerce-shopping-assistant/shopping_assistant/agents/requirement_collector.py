"""Agent 1 - Requirement Collector.

Turns a free-text request ("laptop under 1000 for coding") into a structured
`Requirements` object. If an `input_fn` is supplied (e.g. Python's `input`) it
also asks short follow-up questions for anything important that is missing.

It is rule-based (regular expressions + keyword lists) on purpose: it is fast,
needs no API key, and behaves the same way every time, which makes it testable.
"""
from __future__ import annotations

import re
from typing import Callable, Dict, Iterable, List, Optional, Tuple

from ..catalog import CATEGORY_LABELS
from ..models import Requirements
from .base import BaseAgent

InputFn = Callable[[str], str]

# category -> words that signal it (singular; a trailing "s" is allowed)
CATEGORY_KEYWORDS: Dict[str, List[str]] = {
    "laptop": ["laptop", "notebook", "ultrabook"],
    "headphones": ["headphone", "earbud", "earphone", "headset"],
    "smartphone": ["smartphone", "phone", "mobile"],
    "running_shoes": ["shoe", "sneaker", "trainer"],
    "backpack": ["backpack", "rucksack", "bag"],
}

# need/tag -> phrases that signal it
TAG_KEYWORDS: Dict[str, List[str]] = {
    "coding": ["coding", "programming", "developer", "software development", "code"],
    "gaming": ["gaming", "gamer", "games", "game"],
    "student": ["student", "college", "university", "school", "studying"],
    "travel": ["travel", "traveling", "travelling", "commute", "commuting", "trip", "trips"],
    "office": ["office", "business", "work", "wfh", "meetings", "professional"],
    "creative": ["video editing", "editing", "design", "creative", "creator"],
    "music": ["music", "audio", "listening"],
    "noise-cancelling": ["noise cancelling", "noise-cancelling", "noise canceling",
                         "noise cancellation", "anc"],
    "wireless": ["wireless", "bluetooth"],
    "gym": ["gym", "workout", "workouts", "fitness"],
    "running": ["running", "jogging"],
    "marathon": ["marathon", "race", "racing"],
    "trail": ["trail", "off-road"],
    "hiking": ["hiking", "hike", "trekking", "trek"],
    "daily": ["daily", "everyday", "casual"],
    "photography": ["photography", "photos", "photographer"],
}

# priority word -> phrases that signal it
PRIORITY_KEYWORDS: Dict[str, List[str]] = {
    "battery": ["battery"],
    "light": ["lightweight", "light-weight", "light", "portable", "compact"],
    "camera": ["camera", "cameras"],
    "storage": ["storage", "ssd"],
    "performance": ["performance", "fast", "powerful", "speed"],
    "cushion": ["cushioned", "cushion", "cushioning", "comfortable", "comfort"],
    "capacity": ["spacious", "large capacity", "roomy"],
    "durability": ["durable", "durability", "sturdy", "built to last"],
    "value": ["cheap", "cheapest", "affordable", "value", "inexpensive", "low cost"],
}


def _compile(words: Iterable[str], plural: bool = False) -> "re.Pattern[str]":
    alt = "|".join(re.escape(w) for w in sorted(words, key=len, reverse=True))
    return re.compile(rf"\b(?:{alt}){'s?' if plural else ''}\b", re.IGNORECASE)


_CATEGORY_RE = {c: _compile(w, plural=True) for c, w in CATEGORY_KEYWORDS.items()}
_TAG_RE = {t: _compile(w) for t, w in TAG_KEYWORDS.items()}
_PRIORITY_RE = {p: _compile(w) for p, w in PRIORITY_KEYWORDS.items()}

# A number such as 1000, 1,000, 1.5 or 50k - but NOT when it is really a spec
# ("16gb", "1.5 kg", "10 hours"), which is what the two look-aheads guard against.
_NUM = (r"(\d[\d,]*(?:\.\d+)?)\s*(k\b)?(?![,.]?\d)"
        r"(?!\s*(?:kg|gb|tb|hours?|hrs?|mah|mp|inch(?:es)?|in\b|l\b|litres?|liters?|g\b|mm|km|%))")
_MAX_WORDS = (r"(?:under|below|less than|up to|upto|within|at most|not more than|cheaper than|"
              r"max(?:imum)?(?: budget)?(?: of)?|budget(?: of| is)?|around|about)")
_MIN_WORDS = r"(?:over|above|at least|more than|minimum|min)"

_BETWEEN_RE = re.compile(rf"between\s*\$?\s*{_NUM}\s*(?:and|to|-)\s*\$?\s*{_NUM}", re.IGNORECASE)
_MAX_RE = re.compile(rf"\b{_MAX_WORDS}\s*\$?\s*{_NUM}", re.IGNORECASE)
_MIN_RE = re.compile(rf"\b{_MIN_WORDS}\s*\$\s*{_NUM}", re.IGNORECASE)
_DOLLAR_RE = re.compile(rf"\$\s*{_NUM}")
_BARE_RE = re.compile(rf"^\s*\$?\s*{_NUM}\s*$")


def _amount(number: str, k: Optional[str]) -> float:
    value = float(number.replace(",", ""))
    return value * 1000 if k else value


def detect_category(text: str) -> Optional[str]:
    """Return the category mentioned in `text`.

    If several are mentioned ("laptop bag") the LAST one wins, because in
    English the main noun usually comes last.
    """
    best: Tuple[int, Optional[str]] = (-1, None)
    for category, pattern in _CATEGORY_RE.items():
        for m in pattern.finditer(text):
            if m.start() > best[0]:
                best = (m.start(), category)
    return best[1]


def _detect_ordered(text: str, patterns: Dict[str, "re.Pattern[str]"]) -> List[str]:
    found = []
    for name, pattern in patterns.items():
        m = pattern.search(text)
        if m:
            found.append((m.start(), name))
    return [name for _, name in sorted(found)]


def detect_tags(text: str) -> List[str]:
    return _detect_ordered(text, _TAG_RE)


def detect_priorities(text: str) -> List[str]:
    return _detect_ordered(text, _PRIORITY_RE)


def parse_budget(text: str) -> Tuple[Optional[float], Optional[float]]:
    """Return (min_budget, max_budget) found in the text, either may be None."""
    m = _BETWEEN_RE.search(text)
    if m:
        low, high = _amount(m.group(1), m.group(2)), _amount(m.group(3), m.group(4))
        return (min(low, high), max(low, high))
    low = high = None
    m = _MAX_RE.search(text)
    if m:
        high = _amount(m.group(1), m.group(2))
    m = _MIN_RE.search(text)
    if m:
        low = _amount(m.group(1), m.group(2))
    if low is None and high is None:
        m = _DOLLAR_RE.search(text)
        if m:
            high = _amount(m.group(1), m.group(2))
    return (low, high)


def parse_min_specs(text: str) -> Dict[str, float]:
    """Pick up simple hard requirements such as '16GB RAM' or '512GB SSD'."""
    specs: Dict[str, float] = {}
    m = (re.search(r"(\d+)\s*gb\s*(?:of\s*)?ram", text, re.I)
         or re.search(r"ram\s*(?:of\s*)?(?:at least\s*)?(\d+)\s*gb", text, re.I))
    if m:
        specs["ram_gb"] = float(m.group(1))
    m = re.search(r"(\d+)\s*(gb|tb)\s*(?:ssd|storage)", text, re.I)
    if m:
        specs["storage_gb"] = float(m.group(1)) * (1000 if m.group(2).lower() == "tb" else 1)
    m = (re.search(r"(\d+)\s*(?:hours?|hrs?)\s*(?:of\s*)?battery", text, re.I)
         or re.search(r"battery\s*(?:life\s*)?(?:of\s*)?(?:at least\s*)?(\d+)\s*(?:hours?|hrs?)", text, re.I))
    if m:
        specs["battery_hours"] = float(m.group(1))
    return specs


class RequirementCollectorAgent(BaseAgent):
    name = "RequirementCollector"

    def __init__(self, known_brands: Optional[Iterable[str]] = None, logger=None):
        super().__init__(logger)
        self.known_brands = list(known_brands or [])

    # ------------------------------------------------------------- parsing --
    def _detect_brands(self, text: str) -> List[str]:
        return [b for b in self.known_brands
                if re.search(rf"\b{re.escape(b)}\b", text, re.IGNORECASE)]

    def parse(self, text: str) -> Requirements:
        """Understand a free-text request without asking anything."""
        min_budget, max_budget = parse_budget(text)
        return Requirements(
            raw_query=text,
            category=detect_category(text),
            min_budget=min_budget,
            max_budget=max_budget,
            tags=detect_tags(text),
            brands=self._detect_brands(text),
            min_specs=parse_min_specs(text),
            priorities=detect_priorities(text),
        )

    # ----------------------------------------------------------- follow-up --
    @staticmethod
    def _ask(input_fn: InputFn, prompt: str) -> str:
        try:
            return input_fn(prompt).strip()
        except EOFError:          # e.g. no keyboard attached
            return ""

    def _ask_missing(self, req: Requirements, input_fn: InputFn) -> Requirements:
        if not req.category:
            options = ", ".join(CATEGORY_LABELS.values())
            for attempt in range(2):
                prompt = (f"What are you shopping for? ({options}): " if attempt == 0
                          else f"Sorry, I only know about: {options}. Try again: ")
                answer = self._ask(input_fn, prompt)
                if not answer:
                    break
                req.category = detect_category(answer)
                if req.category:
                    self.log.info("Asked for category -> %s", req.category)
                    break
        if not req.category:
            return req                      # cannot continue without it

        if req.max_budget is None and req.min_budget is None:
            answer = self._ask(input_fn, "What is your maximum budget? (Enter to skip): ")
            if answer:
                low, high = parse_budget(answer)
                m = _BARE_RE.match(answer)
                if high is None and low is None and m:
                    high = _amount(m.group(1), m.group(2))
                req.min_budget, req.max_budget = low, high
                self.log.info("Asked for budget -> min=%s max=%s", low, high)

        if not req.tags:
            answer = self._ask(input_fn, "What will you mainly use it for? e.g. coding, travel (Enter to skip): ")
            if answer:
                req.tags = detect_tags(answer)
                for word in detect_priorities(answer):
                    if word not in req.priorities:
                        req.priorities.append(word)
                self.log.info("Asked for needs -> tags=%s", req.tags)
        return req

    # ----------------------------------------------------------------- run --
    def run(self, query: str, input_fn: Optional[InputFn] = None) -> Requirements:
        req = self.parse(query)
        self.log.info("Parsed query: %s", req.summary())
        if input_fn is not None:
            req = self._ask_missing(req, input_fn)
            self.log.info("After follow-up questions: %s", req.summary())
        return req
