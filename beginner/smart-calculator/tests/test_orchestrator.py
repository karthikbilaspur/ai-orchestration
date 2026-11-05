import json

import pytest

import calculator
from llm_client import OfflineLLM
from orchestrator import PlanError, parse_plan, solve


class StubLLM:
    """Returns canned replies so tests never touch the network."""

    def __init__(self, plan: str, explanation: str = "Done."):
        self.plan, self.explanation, self.calls = plan, explanation, []

    def complete(self, task, system, user):
        self.calls.append(task)
        return self.plan if task == "plan" else self.explanation


PLAN = json.dumps({"steps": [
    {"id": 1, "op": "percent_of", "args": [15, 2500], "description": "15% of 2500"},
    {"id": 2, "op": "add", "args": ["$1", 500], "description": "add 500"},
]})


def test_full_pipeline_with_stub():
    llm = StubLLM(PLAN, "Final answer: 875")
    result = solve("What is 15% of 2,500, and add 500?", llm)
    assert result["final"] == 875
    assert llm.calls == ["plan", "explain"]
    assert result["explanation"] == "Final answer: 875"


def test_parse_plan_strips_markdown_fences():
    assert len(parse_plan("```json\n" + PLAN + "\n```")) == 2


@pytest.mark.parametrize("raw", [
    "no json here",
    "{bad json}",
    '{"steps": []}',
    '{"steps": [{"op": "add"}]}',
    '{"steps": [{"op": "hack", "args": [1]}]}',
    '{"error": "not a math problem"}',
])
def test_parse_plan_rejects_bad_input(raw):
    with pytest.raises(PlanError):
        parse_plan(raw)


def test_empty_question():
    with pytest.raises(PlanError):
        solve("   ", StubLLM(PLAN))


def test_calculator_error_propagates():
    bad = json.dumps({"steps": [{"id": 1, "op": "divide", "args": [1, 0]}]})
    with pytest.raises(calculator.CalculationError):
        solve("1 divided by 0", StubLLM(bad))


def test_offline_llm_example_question():
    result = solve("What is 15% of 2,500, and add 500 to the result?", OfflineLLM())
    assert result["final"] == 875


def test_offline_llm_chain():
    result = solve("12 times 7 minus 4", OfflineLLM())
    assert result["final"] == 80


def test_offline_llm_rejects_non_math():
    with pytest.raises(PlanError):
        solve("Tell me a joke", OfflineLLM())
