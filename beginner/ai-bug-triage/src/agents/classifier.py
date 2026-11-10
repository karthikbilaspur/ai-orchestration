
import re
from ..core.models import ParsedError, Classification

RULES = {
 "dependency": [r"ModuleNotFoundError", r"No module named", r"Cannot find module", r"ERR_MODULE_NOT_FOUND", r"ImportError", r"pip.*not.*found", r"Could not find.*package", r"is not installed", r"UnsatisfiableError", r"npm ERR!.*404", r"EACCES.*node_modules"],
 "syntax": [r"SyntaxError", r"IndentationError", r"Unexpected token", r"Unexpected identifier", r"Missing.*semicolon", r"invalid syntax", r"ParseError", r"Unexpected end of input"],
 "config": [r"KeyError.*config", r"env.*not.*set", r"Missing.*environment", r"Invalid.*configuration", r"yaml.*error", r"JSON.*parse", r"ECONNREFUSED.*config"],
 "network": [r"ConnectionError", r"ECONNREFUSED", r"ETIMEDOUT", r"TimeoutError", r"fetch failed", r"NetworkError", r"DNS", r"404.*Not Found.*http", r"SSLError"],
 "runtime": [r"TypeError", r"ReferenceError", r"NullPointer", r"Cannot read properties of (undefined|null)", r"IndexError", r"KeyError", r"AttributeError", r"ZeroDivisionError", r"ValueError", r"RangeError", r"is not a function", r"is not defined"],
 "logic": [r"AssertionError", r"expected.*but got", r"Assertion.*failed", r"wrong.*output", r"off by one", r"infinite loop", r"returns.*instead of"],
}

class ErrorClassifier:
    def run(self, parsed: ParsedError) -> Classification:
        text = parsed.raw
        scores={k:0 for k in RULES}
        for cat, patterns in RULES.items():
            for p in patterns:
                if re.search(p, text, re.I):
                    scores[cat]+=2
        # Heuristic boosts
        if parsed.exception_type:
            for cat in scores:
                if cat in parsed.exception_type.lower():
                    scores[cat]+=1
        best = max(scores, key=scores.get)
        total = sum(scores.values()) or 1
        if scores[best]==0:
            return Classification(category="unknown", confidence=0.35, reasoning="No strong pattern matched. Treating as unknown and asking Solution Agent to reason generally.", scores=scores)
        conf = round(min(0.95, 0.55 + scores[best]/ (total+2)), 2)
        return Classification(category=best, confidence=conf, reasoning=f"Matched {best} patterns (score {scores[best]}/{total}). Exception: {parsed.exception_type or 'n/a'} — {parsed.message[:120]}", scores=scores)
