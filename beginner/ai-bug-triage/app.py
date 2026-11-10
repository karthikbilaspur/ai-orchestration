
from flask import Flask, request, jsonify, render_template_string
from src.orchestrator import BugTriageOrchestrator
app=Flask(__name__); orch=BugTriageOrchestrator()
HTML=open("templates/index.html").read() if __import__("os").path.exists("templates/index.html") else "<h1>Bug Triage</h1><p>Use POST /api/triage</p>"
@app.get("/")
def home(): return render_template_string(HTML)
@app.post("/api/triage")
def triage():
    raw=(request.get_json(silent=True) or {}).get("error") or request.form.get("error","")
    if not raw: return jsonify({"error":"Paste an error message"}),400
    return jsonify(orch.triage(raw).model_dump())
if __name__=="__main__": app.run(debug=True, port=5000)
