
from ..core.models import Classification
# Conditional Router — pure function, easy to test
ROUTES = {
 "syntax": "syntax_specialist",
 "runtime": "runtime_specialist",
 "dependency": "dependency_specialist",
 "logic": "logic_specialist",
 "config": "config_specialist",
 "network": "network_specialist",
 "unknown": "general_specialist",
}
PROMPTS = {
 "syntax_specialist": "You are a syntax specialist. Find the exact token/indent/bracket causing the parse failure. Fix ONLY that, do not refactor.",
 "runtime_specialist": "You are a runtime specialist. Find the null/undefined, wrong type, or out-of-bounds access. Add a guard / correct type, show before→after.",
 "dependency_specialist": "You are a dependency specialist. Identify missing/wrong-version/conflicting package. Give exact install + version pin + lockfile step.",
 "logic_specialist": "You are a logic specialist. Find the wrong condition / loop / return. Show a failing test case and the corrected logic.",
 "config_specialist": "You are a config specialist. Find missing env var / bad config key. Show .env / config fix without leaking secrets.",
 "network_specialist": "You are a network specialist. Distinguish server-down vs client bug vs auth. Give retry/timeout/check steps.",
 "general_specialist": "You are a general debugger. Reason from the stack trace, list 2 hypotheses, pick the most likely.",
}
class ConditionalRouter:
    def route(self, c: Classification) -> tuple[str,str]:
        key = ROUTES.get(c.category, "general_specialist")
        return key, PROMPTS[key]
