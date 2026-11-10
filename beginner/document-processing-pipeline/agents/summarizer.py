"""Agent 4/5: Summary Agent — concise summary."""
import re
class SummaryAgent:
    def run(self, state: dict) -> dict:
        text = " ".join(state["raw_text"].split()); doc_type = state.get("document_type", "unknown"); fields = state.get("fields", {}); entities = state.get("entities", {})
        sentences = re.split(r"(?<=[.!?])\s+", text); base = " ".join(sentences[:2])[:600]
        parts = [f"This is a {doc_type} document."]
        if base: parts.append(base)
        if fields.get("total"): parts.append(f"Total / amount: {fields['total']}.")
        if fields.get("date"): parts.append(f"Date: {fields['date']}.")
        if entities.get("emails"): parts.append(f"Contact: {entities['emails'][0]}.")
        return {"summary": " ".join(parts)}
