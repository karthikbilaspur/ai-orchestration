"""Test 2: Classifier + Extractor - types, emails, dates, amounts."""
from agents.classifier import ClassificationAgent
from agents.extractor import ExtractionAgent

def _run_classifier(text):
    return ClassificationAgent().run({"raw_text": text})

def _run_extractor(text):
    return ExtractionAgent().run({"raw_text": text})

def test_classifier_types():
    assert _run_classifier("INVOICE Invoice No: 123 Total Due Rs. 5000")["document_type"] == "invoice"
    assert _run_classifier("This Agreement contract parties hereby agree termination clause")["document_type"] == "contract"
    assert _run_classifier("Resume Curriculum Vitae Experience Education Skills")["document_type"] == "resume"
    assert _run_classifier("RECEIPT Thank you for your purchase Transaction Paid")["document_type"] == "receipt"
    assert _run_classifier("hello world no keywords here xyz")["document_type"] == "unknown"
    print("PASS: classifier types")

def test_extractor_entities():
    text = "Invoice No: INV-1 Date: 05 Nov 2026 Total: Rs. 53,100 Email: kai@example.com Phone: +91 98765 43210 To: Kai Karthik"
    r = _run_extractor(text)
    assert "kai@example.com" in r["entities"]["emails"], r
    assert any("53,100" in a for a in r["entities"]["amounts"]), r
    assert any("2026" in d for d in r["entities"]["dates"]), r
    assert r["fields"].get("invoice_no") == "INV-1", r
    print("PASS: extractor entities ->", r["entities"])

if __name__ == "__main__":
    test_classifier_types()
    test_extractor_entities()
    print("All Test 2 passed")
