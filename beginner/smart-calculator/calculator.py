"""The calculator tool. All arithmetic happens here, never inside the LLM."""
import math
from typing import Any, Callable, Dict, List

PRECISION = 10


class CalculationError(Exception):
    """Raised when a step cannot be calculated."""


def _divide(a: float, b: float) -> float:
    if b == 0:
        raise CalculationError("Cannot divide by zero.")
    return a / b


def _modulo(a: float, b: float) -> float:
    if b == 0:
        raise CalculationError("Cannot take modulo by zero.")
    return a % b


def _sqrt(a: float) -> float:
    if a < 0:
        raise CalculationError("Cannot take the square root of a negative number.")
    return math.sqrt(a)


def _power(a: float, b: float) -> float:
    try:
        result = a ** b
    except (OverflowError, ZeroDivisionError) as exc:
        raise CalculationError(f"Power failed: {exc}") from exc
    if isinstance(result, complex):
        raise CalculationError("Result is not a real number.")
    return result


# name -> (function, number of arguments)
OPERATIONS: Dict[str, tuple] = {
    "add": (lambda a, b: a + b, 2),
    "subtract": (lambda a, b: a - b, 2),
    "multiply": (lambda a, b: a * b, 2),
    "divide": (_divide, 2),
    "percent_of": (lambda p, x: p / 100 * x, 2),
    "power": (_power, 2),
    "sqrt": (_sqrt, 1),
    "modulo": (_modulo, 2),
}


def _clean(value: float) -> float:
    """Round away floating point noise (0.1 + 0.2 -> 0.3) and use ints when exact."""
    value = round(value, PRECISION)
    return int(value) if value == int(value) else value


def _resolve(arg: Any, results: Dict[int, float]) -> float:
    """Turn an argument into a number. '$1' means 'result of step 1'."""
    if isinstance(arg, str) and arg.startswith("$"):
        try:
            step_id = int(arg[1:])
        except ValueError as exc:
            raise CalculationError(f"Bad reference: {arg!r}") from exc
        if step_id not in results:
            raise CalculationError(f"Reference {arg} points to a step that has not run yet.")
        return results[step_id]
    if isinstance(arg, bool) or not isinstance(arg, (int, float)):
        raise CalculationError(f"Argument must be a number, got {arg!r}.")
    return arg


def run_step(op: str, args: List[Any], results: Dict[int, float] | None = None) -> float:
    """Run one operation and return the cleaned result."""
    results = results or {}
    if op not in OPERATIONS:
        raise CalculationError(f"Unknown operation: {op!r}")
    func, n_args = OPERATIONS[op]
    if len(args) != n_args:
        raise CalculationError(f"{op} needs {n_args} argument(s), got {len(args)}.")
    numbers = [_resolve(a, results) for a in args]
    return _clean(func(*numbers))


def run_plan(steps: List[dict]) -> List[dict]:
    """Run every step in order. Returns [{id, op, args, description, result}, ...]."""
    results: Dict[int, float] = {}
    output = []
    for step in steps:
        value = run_step(step["op"], step["args"], results)
        results[step["id"]] = value
        output.append({**step, "result": value})
    return output
