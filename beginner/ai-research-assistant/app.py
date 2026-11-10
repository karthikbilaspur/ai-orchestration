"""Flask Web UI for Project 12."""
from flask import Flask, render_template_string, request, jsonify
from src.core.orchestrator import run_research

app = Flask(__name__)

HTML = open("templates/index.html").read() if False else None  # fallback below
TEMPLATE = """
<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>AI Research Assistant</title>
<style>
body{font-family:Inter,system-ui,sans-serif;max-width:900px;margin:0 auto;padding:24px;background:#f8fafc;color:#0f172a}
.card{background:#fff;border-radius:16px;padding:20px;box-shadow:0 4px 20px rgba(0,0,0,.06);margin-bottom:16px}
input{width:100%;padding:14px;border:1px solid #cbd5e1;border-radius:12px;font-size:16px}
button{background:#0f172a;color:#fff;border:0;padding:12px 20px;border-radius:10px;cursor:pointer;font-weight:600}
.badge{display:inline-block;padding:4px 10px;border-radius:999px;font-size:12px;font-weight:700}
.pass{background:#dcfce7}.fail{background:#fee2e2}.warn{background:#fef9c3}
.claim{border-left:4px solid #22c55e;padding:10px 12px;background:#f8fafc;margin:8px 0;border-radius:8px}
.claim.unsupported{border-color:#ef4444}.claim.partial{border-color:#f59e0b}
small{color:#64748b}.flow{font-family:monospace;background:#0f172a;color:#a7f3d0;padding:14px;border-radius:12px;white-space:pre-wrap}
</style></head><body>
<h1>🔍 AI Research Assistant <span style="font-size:14px;color:#64748b">+ Fact Checker</span></h1>
<p>Sequential + Verification • Confidence-based routing • Retry loops</p>
<div class="card"><form method="post"><input name="question" placeholder="e.g. What are benefits and risks of intermittent fasting?" value="{{q}}" required><br><br><button>Run Research →</button></form></div>
{% if result %}
<div class="card"><h2>{{result.title}}</h2>
<span class="badge {{'pass' if result.confidence>=0.75 else 'warn'}}">Confidence {{(result.confidence*100)|int}}% • {{result.status}}</span>
<span class="badge">Retries: {{result.retries_used}}</span>
<p><small>Subtopics: {{result.subtopics|join(', ')}}</small></p>
<div class="flow">User Question → Planner → Researcher → Fact Checker → Confidence Check → {% if result.confidence>=0.75 %}Report ✅{% else %}Research Again ↻ → Report ⚠️{% endif %}</div>
</div>
<div class="card"><h3>📋 Executive Summary</h3><p>{{result.summary}}</p></div>
<div class="card"><h3>✅ Verified Claims</h3>{% for c in result.claims %}<div class="claim {{c.verdict|lower}}"><b>{{c.text}}</b><br><small>Verdict: {{c.verdict}} • Confidence: {{(c.confidence*100)|int}}% • Source: {{c.source}} — “{{c.evidence}}”</small></div>{% endfor %}</div>
<div class="card"><h3>📚 Sources</h3><ul>{% for s in result.sources %}<li>{{s}}</li>{% endfor %}</ul></div>
{% endif %}
<p><small>Try: How does photosynthesis work? • What caused the 2008 financial crisis? • Is coffee good for health?</small></p>
</body></html>
"""

@app.route("/", methods=["GET","POST"])
def index():
    q = ""
    result = None
    if request.method == "POST":
        q = request.form.get("question","").strip()
        if q:
            result = run_research(q)
    return render_template_string(TEMPLATE, q=q, result=result)

@app.route("/api/research", methods=["POST"])
def api():
    data = request.get_json(force=True, silent=True) or {}
    q = data.get("question","").strip()
    if not q:
        return jsonify({"error":"question required"}), 400
    r = run_research(q, confidence_threshold=float(data.get("threshold",0.75)), max_retries=int(data.get("retries",2)))
    return jsonify(r.to_dict())

if __name__ == "__main__":
    app.run(debug=True, port=5000)
