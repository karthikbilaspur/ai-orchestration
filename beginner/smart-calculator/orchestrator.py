"""Coordinates the 7-step pipeline: question -> LLM -> calculator -> LLM -> answer."""
import json
from typing import Any, Dict

import calculator
import config
from logger_setup import get_logger

log = get_logger()


class PlanError(Exception):
    """Raised when the LLM's plan is missing, malformed, or says 'not math'."""


def load_prompt(name: str) -> str:
    return (config.PROMPTS_DIR / f"{name}.txt").read_text(encoding="utf-8")


def parse_plan(raw: str) -> list:
    """Extract and validate the JSON plan returned by the LLM."""
    start, end = raw.find("{"), raw.rfind("}")
    if start == -1 or end == -1:
        raise PlanError("The AI did not return a JSON plan.")
    try:
        data = json.loads(raw[start:end + 1])
    except json.JSONDecodeError as exc:
        raise PlanError(f"The AI returned invalid JSON: {exc}") from exc

    if "error" in data:
        raise PlanError(str(data["error"]))
    steps = data.get("steps")
    if not isinstance(steps, list) or not steps:
        raise PlanError("The plan has no steps.")

    for expected_id, step in enumerate(steps, start=1):
        if not isinstance(step, dict) or not {"op", "args"} <= step.keys():
            raise PlanError(f"Step {expected_id} is malformed.")
        if step["op"] not in calculator.OPERATIONS:
            raise PlanError(f"Step {expected_id} uses unknown operation {step['op']!r}.")
        step["id"] = expected_id  # enforce clean, sequential ids
        step.setdefault("description", f"{step['op']}{tuple(step['args'])}")
    return steps


def solve(question: str, llm) -> Dict[str, Any]:
    """Run the full pipeline and return everything for display."""
    question = question.strip()
    if not question:
        raise PlanError("Please enter a math question.")
    log.info("1. QUESTION: %s", question)

    # 2-3. LLM understands the request and identifies operations
    raw_plan = llm.complete("plan", load_prompt("understand"), question)
    log.info("2. LLM PLAN (raw): %s", raw_plan)
    try:
        steps = parse_plan(raw_plan)
    except PlanError as exc:
        log.warning("3. PLAN REJECTED: %s", exc)
        raise
    log.info("3. OPERATIONS: %s", json.dumps(steps))

    # 4-5. Python calculator runs the operations
    try:
        results = calculator.run_plan(steps)
    except calculator.CalculationError as exc:
        log.error("4. CALCULATOR ERROR: %s", exc)
        raise
    log.info("5. RESULTS: %s", json.dumps(results))

    # 6. LLM explains the results
    explain_input = f"QUESTION: {question}\nRESULTS:{json.dumps(results)}"
    explanation = llm.complete("explain", load_prompt("explain"), explain_input)
    log.info("6. EXPLANATION: %s", explanation)

    # 7. Final answer
    final = results[-1]["result"]
    log.info("7. FINAL ANSWER: %s", final)
    return {"question": question, "steps": results, "explanation": explanation, "final": final}
