"""Agent 3: Extraction Agent — names, dates, amounts, key details."""
import re
EMAIL = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE = re.compile(r"(?:\+91[\s-]?|0)?[6-9]\d{9}|\+?\d[\d\s\-()]{7,}\d")
DATE = re.compile(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{4}-\d{2}-\d{2}\b|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}\b", re.I)
MONEY = re.compile(r"(?:Rs\.?|INR|\u20b9|\$|USD|EUR|\u00a3)\s?[\d,]+(?:\.\d{2})?|\b\d{1,3}(?:,\d{3})+(?:\.\d{2})?\b")
NAME_LABEL = re.compile(r"(?:Name|Client|Customer|To|From|Mr\.?|Ms\.?|Mrs\.?|Attn)[:\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2})")
class ExtractionAgent:
    def run(self, state: dict) -> dict:
        text = state["raw_text"]
        entities = {"emails": sorted(set(EMAIL.findall(text))), "phones": sorted(set(p.strip() for p in PHONE.findall(text))), "dates": sorted(set(DATE.findall(text))), "amounts": sorted(set(MONEY.findall(text))), "names": sorted(set(NAME_LABEL.findall(text)))}
        fields = {}
        for label, key in [("Invoice No", "invoice_no"), ("Invoice Number", "invoice_no"), ("Total", "total"), ("Amount Due", "amount_due"), ("Date", "date"), ("Due Date", "due_date"), ("Company", "company"), ("Address", "address")]:
            m = re.search(rf"{label}\s*[:#-].\s*(.+)", text, re.I)
            if m: fields[key] = m.group(1).strip().splitlines()[0][:120]
        if entities["amounts"] and "total" not in fields: fields["total"] = entities["amounts"][-1]
        if entities["dates"] and "date" not in fields: fields["date"] = entities["dates"][0]
        if entities["emails"] and "email" not in fields: fields["email"] = entities["emails"][0]
        return {"entities": entities, "fields": fields}
# TODO (LLM upgrade): Replace regex with an LLM call here. Keep same return shape.
