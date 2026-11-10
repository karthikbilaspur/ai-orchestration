"""Web UI — upload TXT/PDF, see structured JSON."""
from flask import Flask, request, render_template_string, jsonify
import os, pathlib
from pipeline import DocumentPipeline
app = Flask(__name__); os.makedirs("uploads", exist_ok=True)
HTML = """<!doctype html><html><head><meta charset="utf-8"><title>AI Document Processing Pipeline</title><style>body{font-family:system-ui;max-width:820px;margin:40px auto;padding:0 16px}pre{background:#f4f4f4;padding:16px;border-radius:10px;white-space:pre-wrap}.card{border:1px solid #ddd;border-radius:12px;padding:16px}button{padding:10px 18px;border-radius:8px;background:#111;color:#fff;border:0;cursor:pointer}</style></head><body><h1>AI Document Processing Pipeline</h1><p>Upload TXT / PDF - Reader - Classifier - Extractor - Validator - Summarizer - JSON</p><div class="card"><form method="post" enctype="multipart/form-data"><input type="file" name="file" accept=".txt,.pdf" required> <button>Process Document</button></form></div>{% if result %}<h2>Result: {{ result.document_type }} {% if result.is_valid %}Valid{% else %}Needs review{% endif %}</h2><p>{{ result.summary }}</p><pre>{{ result|tojson(indent=2) }}</pre>{% endif %}</body></html>"""
@app.route("/", methods=["GET","POST"])
def index():
    result = None
    if request.method == "POST":
        f = request.files.get("file")
        if f:
            path = pathlib.Path("uploads") / f.filename; f.save(path); result = DocumentPipeline().run(str(path))
    return render_template_string(HTML, result=result)
@app.route("/api/process", methods=["POST"])
def api():
    f = request.files.get("file")
    if not f: return jsonify({"error":"No file"}), 400
    path = pathlib.Path("uploads") / f.filename; f.save(path); return jsonify(DocumentPipeline().run(str(path)))
if __name__ == "__main__": app.run(debug=True, port=5000)
