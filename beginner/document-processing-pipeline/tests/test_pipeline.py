"""Test 1: End-to-end pipeline - all samples run and return valid JSON structure."""
from pipeline import DocumentPipeline

def test_invoice_end_to_end():
    r = DocumentPipeline().run("samples/invoice_sample.txt")
    assert r["document_type"] == "invoice", r
    assert r["is_valid"] is True, r["validation_errors"]
    assert "53,100" in str(r["fields"]) or "53,100" in str(r["entities"]["amounts"])
    assert r["summary"], "Summary should not be empty"
    print("PASS: invoice end-to-end ->", r["summary"][:100])

def test_all_samples_run():
    for f in ["samples/invoice_sample.txt","samples/contract_sample.txt","samples/resume_sample.txt","samples/receipt_sample.txt"]:
        r = DocumentPipeline().run(f)
        assert r["document_type"] != "", f
        assert "summary" in r and "entities" in r and "fields" in r
        print(f"PASS: {f} -> {r['document_type']} valid={r['is_valid']}")

if __name__ == "__main__":
    test_invoice_end_to_end()
    test_all_samples_run()
    print("All Test 1 passed")
