
from parser import llm_parse_expense
from calculator import calculate_bill

def test_parser():
    msg = "We had dinner for 3480 rupees, including 18% GST. 4 of us splitting, but I want to add a 10% tip."
    parsed = llm_parse_expense(msg)
    assert parsed["total"] == 3480
    assert parsed["gst_percent"] == 18
    assert parsed["tip_percent"] == 10
    assert parsed["num_people"] == 4
    print("test_parser PASSED")

def test_calculator():
    result = calculate_bill(3480, 18, 10, 4)
    assert result["final_total"] == 3828.0
    assert result["per_person"] == 957.0
    print("test_calculator PASSED")

def test_edge_cases():
    r1 = calculate_bill(1000, 0, 0, 2)
    assert r1["per_person"] == 500.0
    r2 = calculate_bill(500, 5, 5, 1)
    assert r2["num_people"] == 1
    print("test_edge_cases PASSED")

if __name__ == "__main__":
    test_parser()
    test_calculator()
    test_edge_cases()
    print("\nAll tests passed!")
