
from ..core.models import ParsedError, Classification, Fix

# Template-based Solution Agent (works offline). Swap _llm_fix() with OpenAI/Anthropic call for real LLM.
TEMPLATES = {
 "dependency": ("Install the missing dependency", "Missing package / import not found.", "pip install {pkg}  # or: npm install {pkg}\n# Pin it: pip freeze > requirements.txt", ["Re-run the failing command", "Check import works: python -c 'import {pkg}'"]),
 "syntax": ("Fix the syntax / indentation error", "Parser failed at the reported line — usually a missing bracket, colon, or bad indent.", "# Fix line {line} in {file}\n# Before: <broken line>\n# After:  <corrected line with matching brackets / colon / indent>", ["Re-run: python -m py_compile {file}", "Run linter / formatter"]),
 "runtime": ("Guard the null / wrong-type access", "Code accessed a property/index on None / undefined / wrong type.", "# Before:\n#   value = obj['key']  # crashes if obj is None\n# After:\n#   value = (obj or {{}}).get('key')  # or: if obj is not None:\n#   if obj is None: raise ValueError('obj must not be None')", ["Add a test with None / empty input", "Re-run the failing case"]),
 "logic": ("Correct the logic / condition", "Code ran but produced the wrong result — condition, loop bound, or return value is off.", "# Write a failing test first, then fix the condition:\n# assert solve(input) == expected  # currently fails\n# Fix: change < / <=, == / is, or return early", ["Run the new failing test — it should pass now", "Run full test suite"]),
 "config": ("Fix missing / invalid config", "Missing env var or bad config key.", "# .env\n# KEY=value  # add the missing key, never commit secrets\n# config.py: os.getenv('KEY', 'safe-default')", ["Restart the app (env loads at startup)", "Verify with: print(os.getenv('KEY') is not None)"]),
 "network": ("Handle connection / timeout", "Service unreachable, timeout, or auth failure — not a code logic bug.", "# Check service health, then add retry + timeout:\n# requests.get(url, timeout=10)  # never omit timeout\n# Retry with backoff for 5xx / timeout only, not for 4xx", ["curl the endpoint manually", "Check logs for ECONNREFUSED vs 401 vs 5xx"]),
 "unknown": ("Reproduce and narrow down", "Not enough signal to pinpoint root cause.", "# 1. Reproduce with minimal input\n# 2. Add logging around the failing line\n# 3. Bisect: comment out half the code until error disappears", ["Create a minimal reproduction", "Paste the full traceback + code around the line"]),
}

class SolutionAgent:
    def run(self, parsed: ParsedError, cls: Classification, route: str, system_prompt: str) -> Fix:
        title, cause, diff, verify = TEMPLATES.get(cls.category, TEMPLATES["unknown"])
        pkg = "pandas"
        import re
        m = re.search(r"No module named ['\"]([^'\"]+)", parsed.raw) or re.search(r"Cannot find module ['\"]([^'\"]+)", parsed.raw)
        if m: pkg = m.group(1).split(".")[0]
        diff = diff.replace('{pkg}', pkg).replace('{line}', str(parsed.line or '?')).replace('{file}', parsed.file or 'file.py')
        verify = [v.replace('{pkg}', pkg) for v in verify]
        return Fix(title=title, root_cause=f"{cause} | Specialist: {route} | {system_prompt}", diff=diff, explanation=f"Error: {parsed.exception_type or ''} {parsed.message}. Location: {parsed.file or 'unknown'}:{parsed.line or '?'}. This fix targets the root cause for a {cls.category} error, not just the symptom.", verification=verify, prevention="Add a regression test + CI check so this class of error fails fast next time.", risk="Low — minimal, targeted change; verify with the steps above.")
