import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orchestrator import SupportOrchestrator  # noqa: E402
from agents.info_agent import InfoAgent  # noqa: E402
from state import ConversationState  # noqa: E402

bot = SupportOrchestrator()
MAIN = "Where is my order? I ordered shoes 3 days ago, Order ID SHOE998, still not delivered!"


def test_main_example_empathy_and_link():
    s = bot.handle(MAIN)
    assert s.order_id == "SHOE998"
    assert s.tracking["status"] == "Out for delivery"
    assert "sorry" in s.reply.lower()
    assert "https://track.example.com/SHOE998" in s.reply
    assert not s.escalate


def test_order_id_extraction():
    s = InfoAgent().run(ConversationState(message="my id is shoe101 pls"))
    assert s.order_id == "SHOE101"


def test_refund_policy():
    s = bot.handle("I want my money back for order SHOE101")
    assert s.intent == "refund"
    assert "refund policy" in s.reply.lower()


def test_calm_status():
    s = bot.handle("Can you tell me the status of order SHOE202?")
    assert "Shipped" in s.reply


def test_missing_order_id_asks_for_it():
    s = bot.handle("Where is my package?")
    assert "Order ID" in s.reply


def test_unknown_order_escalates():
    s = bot.handle("Where is my order ZZZ999?")
    assert s.escalate


def test_gibberish_escalates():
    s = bot.handle("hello")
    assert s.escalate
