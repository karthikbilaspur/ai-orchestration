# Project 14 — AI Document Processing Pipeline
**Time:** 2–3 hours | **Focus:** Pipeline orchestration

Upload a TXT / PDF and automatically extract useful information.

## Pipeline
```
Document
   |
Reader
   |
Classifier
   |
Extractor
   |
Validator
   |
Summarizer
   |
Structured JSON Output
```

## Agents
1. **Document Reader** – reads uploaded TXT / PDF text.
2. **Classification Agent** – identifies document type.
3. **Extraction Agent** – extracts names, dates, amounts and key details.
4. **Summary Agent** – creates a concise summary.
5. **Validation Agent** – checks required fields.

## Quick Start
```bash
pip install -r requirements.txt
# CLI
python main.py samples/invoice_sample.txt
python main.py samples/contract_sample.txt --output output/result.json
python main.py samples/resume_sample.txt --pretty

# Web UI
python app.py
# open http://localhost:5000
```

## What you'll learn
- Document pipelines, structured extraction, validation
- Orchestration: sequential agents with a shared state dict
- Rule-based + LLM-ready extraction (swap in OpenAI / local LLM in agents/extractor.py)

## Output
Structured JSON: document_type, confidence, entities, fields, missing_fields, is_valid, summary, validation_errors
