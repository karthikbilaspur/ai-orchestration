
from src.orchestrator import BugTriageOrchestrator
o=BugTriageOrchestrator()
def test_dependency_routing():
    r=o.triage("ModuleNotFoundError: No module named 'pandas'")
    assert r.classification.category=="dependency"; assert r.route=="dependency_specialist"; assert "pandas" in r.fix.diff
def test_syntax_routing():
    r=o.triage("SyntaxError: expected ':'\n  File \"app.py\", line 10")
    assert r.classification.category=="syntax"
def test_runtime_routing():
    r=o.triage("TypeError: Cannot read properties of undefined (reading 'map')")
    assert r.classification.category=="runtime"; assert r.review.verdict=="APPROVED"
def test_log_analyzer_extracts_file_line():
    r=o.triage(open("examples/python_traceback.txt").read())
    assert r.parsed.file=="main.py" and r.parsed.line==42
