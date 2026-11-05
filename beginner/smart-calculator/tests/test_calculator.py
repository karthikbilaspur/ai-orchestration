import pytest

from calculator import CalculationError, run_plan, run_step


def test_basic_ops():
    assert run_step("add", [2, 3]) == 5
    assert run_step("subtract", [10, 4]) == 6
    assert run_step("multiply", [6, 7]) == 42
    assert run_step("divide", [9, 3]) == 3
    assert run_step("power", [2, 10]) == 1024
    assert run_step("sqrt", [81]) == 9
    assert run_step("modulo", [10, 3]) == 1


def test_percent_of():
    assert run_step("percent_of", [15, 2500]) == 375


def test_float_noise_is_cleaned():
    assert run_step("add", [0.1, 0.2]) == 0.3


def test_divide_by_zero():
    with pytest.raises(CalculationError):
        run_step("divide", [1, 0])


def test_negative_sqrt():
    with pytest.raises(CalculationError):
        run_step("sqrt", [-4])


def test_unknown_operation_and_wrong_arg_count():
    with pytest.raises(CalculationError):
        run_step("log", [1])
    with pytest.raises(CalculationError):
        run_step("add", [1])


def test_non_numeric_argument_rejected():
    with pytest.raises(CalculationError):
        run_step("add", ["abc", 1])
    with pytest.raises(CalculationError):
        run_step("add", [True, 1])


def test_plan_with_references():
    steps = [
        {"id": 1, "op": "percent_of", "args": [15, 2500], "description": "x"},
        {"id": 2, "op": "add", "args": ["$1", 500], "description": "y"},
    ]
    out = run_plan(steps)
    assert [s["result"] for s in out] == [375, 875]


def test_bad_reference():
    with pytest.raises(CalculationError):
        run_plan([{"id": 1, "op": "add", "args": ["$5", 1], "description": ""}])
