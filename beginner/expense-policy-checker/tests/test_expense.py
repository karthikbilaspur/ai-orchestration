import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import batch  # noqa: E402
import config  # noqa: E402
from agents.parser_agent import detect_bill, find_amounts  # noqa: E402
from orchestrator import ExpenseOrchestrator  # noqa: E402

MAIN = "Hi, spent Rs. 1200 on client dinner at Toit, Bangalore. No bill attached."


def bot():
    return ExpenseOrchestrator()          # fresh instance = fresh duplicate memory


def decide(msg, **kw):
    return bot().process(msg, **kw)


def test_task_example_exact_output():
    s = decide(MAIN)
    assert s.result() == {"decision": "Rejected",
                          "message": "Rejected as per policy: Bill mandatory above Rs 1000"}
    assert s.rule_id == "R1"


def test_parser_fields_for_task_example():
    s = decide(MAIN)
    assert (s.amount, s.category, s.bill, s.place, s.city) == (1200, "food", "No", "Toit", "Bangalore")
    assert s.client_related and s.currency == "INR"


def test_bill_negation_trap():
    assert detect_bill("No bill attached.", []) == "No"          # contains "bill attached"
    assert detect_bill("Bill attached.", []) == "Yes"
    assert detect_bill("bill is not available", []) == "No"
    assert detect_bill("I lost the receipt", []) == "No"
    assert detect_bill("dinner with client", []) == "Unknown"
    assert detect_bill("no bill", ["photo.jpg"]) == "Yes"        # a real attachment wins


def test_amount_formats():
    for text, expected in [("Rs. 1,200", 1200), ("₹1200", 1200), ("INR 1200.50", 1200.5),
                           ("Rs 1.5k", 1500), ("1200 rupees", 1200), ("Rs.350/-", 350),
                           ("spent 450 on tea", 450)]:
        assert [v for v, _ in find_amounts(text)] == [expected], text


def test_boundaries():
    assert decide("Dinner Rs 1000 at X, no bill").decision == "Manager Review"     # not above 1000
    assert decide("Dinner Rs 1001 at X, no bill").decision == "Rejected"
    assert decide("Lunch Rs 499 at X, no bill").decision == "Approved"
    assert decide("Lunch Rs 500 at X, no bill").decision == "Manager Review"       # not below 500


def test_bill_present_goes_to_manager():
    s = decide("Dinner Rs 1200 at Toit. Bill attached.")
    assert s.decision == "Manager Review" and s.rule_id == "R3"


def test_multiple_amounts_and_missing_amount_and_foreign_currency():
    assert decide("Rs 800 dinner and Rs 700 cab").rule_id == "R0-MULTI-AMOUNT"
    assert decide("spent some money on dinner").decision == "Need More Info"
    assert decide("Flight $250 ticket attached").rule_id == "R0-CURRENCY"


def test_unknown_bill_above_limit_asks_then_strict_mode_follows_spec():
    assert decide("Client dinner Rs 5000 at Karavalli").decision == "Need More Info"
    config.ASK_WHEN_BILL_UNKNOWN = False
    try:
        assert decide("Client dinner Rs 5000 at Karavalli").decision == "Manager Review"
    finally:
        config.ASK_WHEN_BILL_UNKNOWN = True


def test_duplicate_detection():
    b = bot()
    first = b.process("Lunch Rs 300 at Toit", sender="Amit")
    again = b.process("Lunch Rs 300 at Toit", sender="Amit")
    other = b.process("Lunch Rs 300 at Toit", sender="Riya")
    assert first.decision == "Approved" and again.rule_id == "R0-DUPLICATE" and other.decision == "Approved"


def test_rejected_claim_can_be_resubmitted_with_bill():
    b = bot()
    assert b.process("Dinner Rs 1200 at Toit, no bill", sender="Amit").decision == "Rejected"
    again = b.process("Dinner Rs 1200 at Toit", sender="Amit", attachments=["bill.jpg"])
    assert again.decision == "Manager Review" and again.rule_id == "R3"


def test_place_variants():
    assert decide("Taxi from airport Rs 500").place == "Airport"
    assert decide("Paid Rs 350 for Uber to office").place == "Uber"
    assert decide("Rs 300 lunch at Third Wave Coffee, Bangalore").place == "Third Wave Coffee"


def test_batch_and_audit_files(tmp_path):
    rows = batch.run_batch(bot(), batch.load(config.BASE_DIR / "sample_expenses.json"))
    d = {r["id"]: r["decision"] for r in rows}
    assert d["E001"] == "Rejected" and d["E002"] == "Approved" and d["E003"] == "Manager Review"
    assert d["E004"] == "Manager Review" and d["E005"] == "Manager Review"
    assert d["E009"] == "Need More Info" and d["E010"] == "Manager Review"
    assert {r["id"]: r["rule"] for r in rows}["E010"] == "R0-DUPLICATE"
    batch.write_outputs(rows, tmp_path)
    assert (tmp_path / "decisions.csv").exists()
    assert json.loads((tmp_path / "results.json").read_text())[0]["rule"] == "R1"
