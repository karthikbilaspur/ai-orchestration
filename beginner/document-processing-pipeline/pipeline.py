"""Orchestrator — wires agents together in order."""
from agents.reader import DocumentReader
from agents.classifier import ClassificationAgent
from agents.extractor import ExtractionAgent
from agents.validator import ValidationAgent
from agents.summarizer import SummaryAgent
class DocumentPipeline:
    def __init__(self):
        self.reader = DocumentReader()
        self.classifier = ClassificationAgent()
        self.extractor = ExtractionAgent()
        self.validator = ValidationAgent()
        self.summarizer = SummaryAgent()
    def run(self, file_path: str) -> dict:
        state = {"file_path": file_path}
        state.update(self.reader.run(state))
        state.update(self.classifier.run(state))
        state.update(self.extractor.run(state))
        state.update(self.validator.run(state))
        state.update(self.summarizer.run(state))
        return {
            "file": state["file_path"],
            "document_type": state["document_type"],
            "classification_confidence": state["confidence"],
            "classification_reason": state.get("classification_reason", ""),
            "entities": state["entities"],
            "fields": state["fields"],
            "missing_fields": state["missing_fields"],
            "is_valid": state["is_valid"],
            "validation_errors": state["validation_errors"],
            "summary": state["summary"],
            "word_count": state["word_count"],
            "char_count": state["char_count"],
        }
