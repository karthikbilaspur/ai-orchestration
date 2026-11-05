import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import batch  # noqa: E402
import config  # noqa: E402
from orchestrator import ScreeningOrchestrator  # noqa: E402
from skills_taxonomy import find_skills  # noqa: E402

bot = ScreeningOrchestrator()
ROHAN = ("Resume: Name: Rohan. Skills: Python, Excel. Project: Made a calculator app. "
         "No AI experience.")
JD = "Need Python + AI/LLM intern"


def test_task_example_exact_output():
    s = bot.screen(ROHAN, JD)
    assert s.result() == {"status": "Rejected", "reason": "No AI/LLM skills"}
    assert s.match_level == "Weak Match"
    assert s.score is not None and s.score < config.REVIEW_SCORE   # Scorer did run
    assert len(s.reason_lines) == 2


def test_no_python_rejects_and_stops():
    s = bot.screen("Name: Vikram. Skills: Java, SQL, Machine Learning.", JD)
    assert s.result() == {"status": "Rejected", "reason": "No Python skills"}
    assert s.stopped_early and s.score is None                      # Scorer skipped


def test_strong_candidate_shortlisted():
    s = bot.screen("Name: Anita. Skills: Python, LangChain, RAG, Git, FastAPI. "
                   "Project: Built a RAG chatbot with OpenAI. Experience: AI intern.", JD)
    assert s.status == "Shortlisted" and s.score >= config.SHORTLIST_SCORE


def test_weak_match_capped_and_sent_to_review():
    s = bot.screen("Name: Sam. Skills: Python, SQL, Git, Flask, Pandas. Project: Built a REST API. "
                   "Experience: Backend intern. No machine learning or LLM experience.", JD)
    assert s.status == "Weak Match" and s.score == config.WEAK_MATCH_CAP


def test_negation_is_not_counted_as_skill():
    found, negated = find_skills("No AI experience.")
    assert "AI" not in found and "AI" in negated
    found, _ = find_skills("Interested in learning AI someday.")
    assert "AI" not in found


def test_word_boundaries():
    found, _ = find_skills("I use OpenAI and JavaScript daily")
    assert "AI" not in found and "Java" not in found
    assert "LLM" in found and "JavaScript" in found


def test_python_version_token_and_free_text_resume():
    s = bot.screen("Skills: Python 3, Git", JD)
    assert "Python" in s.skills
    s = bot.screen("Arjun here. I know Python and fine-tuned transformers with PyTorch "
                   "in an NLP project during my internship.", JD)
    assert s.status == "Shortlisted"


def test_empty_resume():
    s = bot.screen("   ", JD)
    assert s.result() == {"status": "Rejected", "reason": "Empty resume"}


def test_batch_runs_all_samples():
    rows = batch.run_batch(bot, batch.load_json(config.BASE_DIR / "sample_resumes.json"), JD)
    assert len(rows) == 7
    statuses = {r["id"]: r["status"] for r in rows}
    assert statuses["R001"] == "Rejected" and statuses["R002"] == "Shortlisted"
    assert statuses["R004"] == "Weak Match"
