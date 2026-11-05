"""Agent 1: turn a messy chat message into Amount, Category, Bill, Place.

Pure regex. An optional LLM is used ONLY if no amount can be found, and its answer must
literally appear in the message, so it can never invent a number.
"""
import json
import re

from llm import LLMClient
from state import ExpenseState

# ---------------------------------------------------------------- amount
_NUM = r"(?P<num>\d[\d,]*(?:\.\d+)?)(?P<k>k(?![A-Za-z]))?"
_PREFIXED = re.compile(r"(?<![A-Za-z])(?P<cur>rs\.?|inr|₹|\$|usd|€|eur|rupees?)\s*" + _NUM, re.I)
_SUFFIXED = re.compile(_NUM + r"\s*(?P<cur>rs\b|inr\b|rupees?\b|/-|usd\b|eur\b)", re.I)
_BARE = re.compile(r"\b(?:spent|paid|cost|costs|total|of|for)\s+(?P<num>\d[\d,]*(?:\.\d+)?)(?P<k>k(?![A-Za-z]))?\b", re.I)


def _currency(token: str) -> str:
    t = token.lower()
    if t in ("$", "usd"):
        return "USD"
    if t in ("€", "eur"):
        return "EUR"
    return "INR"


def _value(m) -> float:
    v = float(m.group("num").replace(",", ""))
    return v * 1000 if m.group("k") else v


def find_amounts(text: str):
    """Return (list of (value, currency)) with duplicates (same number matched twice) removed."""
    found = {}
    for rx in (_PREFIXED, _SUFFIXED):
        for m in rx.finditer(text):
            found.setdefault(m.start("num"), (_value(m), _currency(m.group("cur"))))
    if not found:
        for m in _BARE.finditer(text):
            found.setdefault(m.start("num"), (_value(m), "INR"))
    return list(found.values())


# ---------------------------------------------------------------- bill
# Order matters: "No bill attached" contains the words "bill attached", so denials are checked first.
_BILL_NO = [re.compile(p, re.I) for p in (
    r"\bno\s+(?:bill|receipt|invoice|proof)s?\b",
    r"\bwithout\s+(?:a\s+|any\s+|the\s+)?(?:bill|receipt|invoice)s?\b",
    r"\b(?:bill|receipt|invoice)s?\s+(?:is\s+|was\s+|are\s+)?(?:not|n't)\s+(?:available|attached|there|provided|with me|taken)\b",
    r"\b(?:bill|receipt|invoice)s?\s+(?:is\s+)?(?:missing|lost)\b",
    r"\b(?:lost|forgot|missed|didn'?t get|did not get|didn'?t take|don'?t have|do not have|haven'?t got|have no)\s+(?:to\s+)?(?:the\s+|a\s+|any\s+|my\s+)?(?:bill|receipt|invoice)s?\b",
    r"\bnot\s+attach(?:ed|ing)\b",
    r"\bbill\s*:\s*no\b",
)]
_BILL_YES = [re.compile(p, re.I) for p in (
    r"\b(?:bill|receipt|invoice)s?\s+(?:is\s+|are\s+)?(?:attached|enclosed)\b",
    r"\battached\s+(?:the\s+|a\s+)?(?:bill|receipt|invoice)\b",
    r"\bplease find\s+(?:the\s+)?(?:bill|receipt|invoice)\b",
    r"\b(?:have|got)\s+(?:the\s+)?(?:bill|receipt|invoice)\b",
    r"\bbill\s*:\s*yes\b",
)]


def detect_bill(text: str, attachments: list) -> str:
    if attachments:                       # a real file/image from WhatsApp/Slack beats any wording
        return "Yes"
    if any(p.search(text) for p in _BILL_NO):
        return "No"
    if any(p.search(text) for p in _BILL_YES):
        return "Yes"
    return "Unknown"


# ---------------------------------------------------------------- category / place
_CATEGORIES = {
    "food": r"dinner|lunch|breakfast|meals?|food|restaurant|cafe|coffee|snacks?|tea|biryani|pizza|treat|swiggy|zomato",
    "travel": r"cab|uber|ola|taxi|flights?|train|bus|metro|fuel|petrol|diesel|toll|parking|airport|auto|ticket",
    "accommodation": r"hotel|stay|lodging|airbnb|room rent",
    "office_supplies": r"stationery|supplies|printer|toner|courier",
    "software": r"subscription|licen[cs]e|saas|domain|hosting",
}
_CAT_RX = {k: re.compile(rf"(?<![A-Za-z])(?:{v})(?![A-Za-z])", re.I) for k, v in _CATEGORIES.items()}

_PLACE_CAP = re.compile(r"(?:\b(?i:at|from)|@)\s+([A-Z][\w&'\-]*(?:\s+(?:&\s+)?[A-Z][\w&'\-]*)*)")
_PLACE_LOW = re.compile(r"(?:\b(?i:at|from)|@)\s+(?!\d)(?!(?:the|a|an|my|our|office|home|work)\b)([a-z][\w&'\-]*)")
_VENDOR = re.compile(r"\b(uber|ola|swiggy|zomato|amazon|irctc|makemytrip|rapido)\b", re.I)
_CITY = re.compile(r"[A-Z][A-Za-z]+(?:\s[A-Z][A-Za-z]+)?")


def detect_category(text: str) -> str:
    scores = {k: len(rx.findall(text)) for k, rx in _CAT_RX.items()}
    best = max(scores, key=scores.get)         # ties keep dict order
    return best if scores[best] else "other"


def detect_place(text: str):
    m = _PLACE_CAP.search(text)
    if m:
        place = m.group(1)
        rest = text[m.end():]
        c = re.match(r"\s*,\s*(" + _CITY.pattern + ")", rest)
        city = c.group(1) if c else None
        if not city:
            c = re.search(r"\bin\s+(" + _CITY.pattern + ")", text)
            city = c.group(1) if c else None
        return place, city
    m = _PLACE_LOW.search(text)
    if m:
        return m.group(1).title(), None
    m = _VENDOR.search(text)
    return (m.group(1).title(), None) if m else (None, None)


class ParserAgent:
    def __init__(self, llm: LLMClient = None):
        self.llm = llm or LLMClient()

    def run(self, s: ExpenseState) -> ExpenseState:
        text = s.raw
        amounts = find_amounts(text)
        if not amounts and self.llm.available:
            amounts = self._llm_amount(text, s)

        distinct = sorted({v for v, _ in amounts})
        if len(distinct) > 1:
            s.amounts_found = distinct
            s.flags.append("multiple_amounts")
        elif distinct:
            s.amount = distinct[0]
            s.currency = amounts[0][1]
            s.amounts_found = distinct

        s.bill = detect_bill(text, s.attachments)
        if s.attachments and any(p.search(text) for p in _BILL_NO):
            s.flags.append("text_says_no_bill_but_file_attached")
        s.category = detect_category(text)
        s.client_related = bool(re.search(r"\bclient\b", text, re.I))
        s.place, s.city = detect_place(text)
        return s

    def _llm_amount(self, text: str, s: ExpenseState):
        try:
            raw = self.llm.complete('Extract the expense amount. Reply ONLY JSON: {"amount": number or null}', text)
            amount = json.loads(re.sub(r"```json|```", "", raw).strip()).get("amount")
            if isinstance(amount, (int, float)) and amount > 0 and \
                    str(int(amount)) in text.replace(",", ""):        # must really be in the message
                return [(float(amount), "INR")]
        except Exception as exc:
            s.errors.append(f"parser LLM fallback failed: {exc}")
        return []
