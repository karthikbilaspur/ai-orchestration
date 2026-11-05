import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config  # noqa: E402
config.SIMULATED_LATENCY = 0
from orchestrator import MeetingOrchestrator  # noqa: E402
from parser import parse_request  # noqa: E402
from agents.questions_agent import QuestionsAgent  # noqa: E402

MAIN = "I have a meeting with Flipkart team at 2 PM about AI integration"
bot = MeetingOrchestrator()


def test_parse_main_example():
    s = parse_request(MAIN)
    assert (s.company, s.time_label, s.time_minutes, s.topic) == ("Flipkart", "2 PM", 840, "AI integration")
    assert s.category == "ai_integration" and not s.errors


def test_parse_variants():
    s = parse_request("Call with Zomato team at 10:30 AM about cloud cost optimization")
    assert s.company == "Zomato" and s.time_label == "10:30 AM" and s.time_minutes == 630
    assert s.category == "generic"
    s = parse_request("Quick sync with Acme at 9 AM")
    assert s.company == "Acme" and s.topic is None and "no topic found" in s.errors


def test_brief_structure_for_flipkart():
    s = bot.brief(MAIN)
    b = s.brief
    assert "## 1. Intro" in b and "## 2. Questions to ask" in b
    assert len(s.tech["points"]) == 3 and s.tech["kind"] == "researched"
    assert len(s.questions) == 5
    assert all(f"\n{i}. **" in b for i in range(1, 6))
    assert b.count("\n") + 1 <= config.MAX_BRIEF_LINES


def test_agents_really_run_in_parallel():
    config.SIMULATED_LATENCY = 0.3
    try:
        s = bot.brief(MAIN)
    finally:
        config.SIMULATED_LATENCY = 0
    assert sum(s.timings.values()) >= 0.6
    assert s.wall_time < 0.5          # sequential would be >= 0.6


def test_tech_agent_failure_still_gives_brief():
    original = bot.tech_agent.run
    bot.tech_agent.run = lambda ctx: (_ for _ in ()).throw(RuntimeError("search down"))
    try:
        s = bot.brief(MAIN)
    finally:
        bot.tech_agent.run = original
    assert "Tech snapshot unavailable" in s.brief and len(s.questions) == 5
    assert any("TechStackAgent failed" in e for e in s.errors)


def test_questions_agent_failure_uses_fallback():
    original = bot.questions_agent.run
    bot.questions_agent.run = lambda ctx: (_ for _ in ()).throw(RuntimeError("llm down"))
    try:
        s = bot.brief(MAIN)
    finally:
        bot.questions_agent.run = original
    assert len(s.questions) == 5 and len(s.tech["points"]) == 3


def test_unknown_company_is_labelled_as_assumption():
    s = bot.brief("Meeting with Infosys team at 4 PM about LLM chatbot rollout")
    assert s.tech["kind"] == "assumed" and "assumption" in s.tech["points"][0]


def test_question_validation():
    good = [{"q": f"Q{i}?", "why": "x"} for i in range(5)]
    assert QuestionsAgent._valid(good)
    assert not QuestionsAgent._valid(good[:4])
    assert not QuestionsAgent._valid([{"q": "no mark", "why": "x"}] * 5)


def test_day_is_sorted_by_time():
    states = bot.brief_day(open(os.path.join(config.BASE_DIR, "sample_requests.txt")).read().splitlines())
    assert [s.company for s in states] == ["Acme", "Zomato", "Flipkart", "Infosys"]
