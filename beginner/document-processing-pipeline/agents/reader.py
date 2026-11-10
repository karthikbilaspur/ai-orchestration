"""Agent 1: Document Reader — reads TXT / PDF text."""
import pathlib
class DocumentReader:
    def run(self, state: dict) -> dict:
        path = pathlib.Path(state["file_path"])
        ext = path.suffix.lower()
        if ext == ".txt":
            text = path.read_text(encoding="utf-8", errors="ignore")
        elif ext == ".pdf":
            text = self._read_pdf(path)
        else:
            text = path.read_text(encoding="utf-8", errors="ignore")
        return {"raw_text": text, "char_count": len(text), "word_count": len(text.split())}
    def _read_pdf(self, path):
        try:
            from PyPDF2 import PdfReader
        except ImportError:
            raise RuntimeError("PyPDF2 not installed. Run: pip install PyPDF2")
        reader = PdfReader(str(path))
        return "\n".join((page.extract_text() or "") for page in reader.pages)
