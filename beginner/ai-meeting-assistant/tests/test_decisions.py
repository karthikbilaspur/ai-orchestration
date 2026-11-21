import unittest

from meeting_assistant.agents.decisions import DecisionExtractorAgent
from tests.helpers import SAMPLE


class DecisionTests(unittest.TestCase):
    agent = DecisionExtractorAgent()

    def texts(self, transcript):
        return [d["text"] for d in self.agent.extract(transcript)]

    def test_labelled_decision(self):
        self.assertEqual(self.texts("Decision: use option B"), ["use option B"])

    def test_marker_decisions(self):
        t = self.texts("We agreed to move the launch.\nBudget approved for design work.\nWe will proceed with vendor A.")
        self.assertEqual(len(t), 3)

    def test_negated_questions_and_conditionals_ignored(self):
        t = self.texts("We haven't decided on pricing yet.\nHave we approved the plan?\n"
                       "If we decide to go, tell me.\nWe have not agreed on a date.\nNobody has decided anything yet.")
        self.assertEqual(t, [])

    def test_short_confirmations_ignored(self):
        self.assertEqual(self.texts("Agreed.\nApproved."), [])

    def test_duplicates_removed(self):
        self.assertEqual(len(self.texts("Budget approved today.\nBudget approved today.")), 1)

    def test_speaker_and_timestamp_are_kept(self):
        d = self.agent.extract("[00:01:10] Priya: We decided to delay the launch.")[0]
        self.assertEqual((d["speaker"], d["timestamp"]), ("Priya", "00:01:10"))

    def test_sample_transcript(self):
        self.assertEqual(len(self.texts(SAMPLE)), 2)


if __name__ == "__main__":
    unittest.main()
