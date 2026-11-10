"""Test 3: Validator + Summarizer + Reader - missing fields, empty doc, PDF/TXT reading."""
from agents.validator import ValidationAgent
from agents.summarizer import SummaryAgent
from agents.reader import DocumentReader

def test_validator_missing_fields():
    # Invoice without invoice_no/total/date should fail
    state = {"document_type": "invoice", "fields": {}, "entities": {"amounts": [], "dates": [], "emails": []}, "raw_text": "some invoice text"}
    r = ValidationAgent().run(state)
    assert r["is_valid"] is False
    assert len(r["missing_fields"]) >= 1
    assert "Missing required field" in r["validation_errors"][0]
    print("PASS: validator catches missing fields ->", r["missing_fields"])

def test_validator_passes_when_fields_present():
    state = {"document_type": "invoice", "fields": {"invoice_no": "INV-1", "total": "Rs. 100", "date": "05 Nov 2026"}, "entities": {}, "raw_text": "invoice"}
    r = ValidationAgent().run(state)
    assert r["is_valid"] is True and r["missing_fields"] == []
    print("PASS: validator passes when complete")

def test_validator_empty_document():
    r = ValidationAgent().run({"document_type": "unknown", "fields": {}, "entities": {}, "raw_text": "   "})
    assert r["is_valid"] is False
    assert "Document is empty" in r["validation_errors"]
    print("PASS: validator catches empty doc")

def test_summarizer_and_reader():
    r = DocumentReader().run({"file_path": "samples/invoice_sample.txt"})
    assert r["word_count"] > 10 and r["char_count"] > 50
    s = SummaryAgent().run({"raw_text": "Hello world. This is a test. Third sentence.", "document_type": "invoice", "fields": {"total": "Rs. 100"}, "entities": {"emails": ["a@b.com"]}})
    assert "invoice" in s["summary"].lower() and "Rs. 100" in s["summary"]
    print("PASS: summarizer + reader ->", s["summary"][:100])

if __name__ == "__main__":
    test_validator_missing_fields()
    test_validator_passes_when_fields_present()
    test_validator_empty_document()
    test_summarizer_and_reader()
    print("All Test 3 passed")
