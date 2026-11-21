import unittest

from meeting_assistant.agents.summarizer import SummarizerAgent
from tests.helpers import SAMPLE


class SummarizerTests(unittest.TestCase):
    agent = SummarizerAgent()

    def test_basic_summary(self):
        self.assertIn("Budget", self.agent.summarize("Budget approved. Launch next week."))

    def test_empty_input(self):
        self.assertEqual(self.agent.summarize(""), "No transcript content supplied.")
        self.assertEqual(self.agent.summarize("Ok. Yes."), "No transcript content supplied.")

    def test_short_vs_detailed_length(self):
        short = self.agent.select(SAMPLE, "short")
        detailed = self.agent.select(SAMPLE, "detailed")
        self.assertLessEqual(len(short), 3)
        self.assertGreater(len(detailed), len(short))

    def test_selection_keeps_original_order_and_is_deterministic(self):
        picked = self.agent.select(SAMPLE, "detailed")
        idx = [s["index"] for s in picked]
        self.assertEqual(idx, sorted(idx))
        self.assertEqual(idx, [s["index"] for s in self.agent.select(SAMPLE, "detailed")])

    def test_short_is_paragraph_and_detailed_is_bullets(self):
        self.assertNotIn("\n", self.agent.summarize(SAMPLE, "short"))
        lines = self.agent.summarize(SAMPLE, "detailed").splitlines()
        self.assertTrue(all(line.startswith("- ") for line in lines))

    def test_filler_is_not_selected(self):
        texts = [s["text"] for s in self.agent.select(SAMPLE, "detailed")]
        self.assertFalse(any(t.startswith("Good morning") for t in texts))

    def test_decisions_are_favoured(self):
        text = " ".join(s["text"] for s in self.agent.select(SAMPLE, "short"))
        self.assertIn("decided", text)

    def test_key_topics(self):
        topics = self.agent.key_topics(SAMPLE)
        self.assertIn("launch", topics)
        self.assertIn("onboarding", topics)
        self.assertLessEqual(len(topics), 5)
        self.assertNotIn("the", topics)

    def test_short_transcript_returns_something(self):
        self.assertTrue(self.agent.summarize("Budget approved."))


if __name__ == "__main__":
    unittest.main()
