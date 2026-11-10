"""Agent 5: Validation Agent — checks required fields."""
REQUIRED_FIELDS = {"invoice": ["invoice_no", "total", "date"], "contract": ["date"], "resume": ["email"], "receipt": ["total", "date"], "letter": ["date"], "report": [], "unknown": []}
class ValidationAgent:
    def run(self, state: dict) -> dict:
        doc_type = state.get("document_type", "unknown"); fields = state.get("fields", {}); entities = state.get("entities", {})
        required = REQUIRED_FIELDS.get(doc_type, []); missing, errors = [], []
        for f in required:
            if f not in fields:
                if f == "total" and entities.get("amounts"): continue
                if f == "date" and entities.get("dates"): continue
                if f == "email" and entities.get("emails"): continue
                missing.append(f); errors.append(f"Missing required field: {f}")
        if not state.get("raw_text", "").strip(): errors.append("Document is empty"); missing.append("content")
        return {"missing_fields": missing, "validation_errors": errors, "is_valid": len(errors) == 0}
