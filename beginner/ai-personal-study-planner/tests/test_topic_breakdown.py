import unittest

from study_planner.agents.topic_breakdown import ADVANCED, FOUNDATIONS, REVISION, TopicBreakdownAgent
from tests.helpers import make_req


class TopicTests(unittest.TestCase):
    agent = TopicBreakdownAgent()

    def names(self, topics):
        return [t["topic"] for t in topics]

    def test_domain_detection(self):
        d = self.agent.detect_domain
        self.assertEqual(d("Python programming"), "programming")
        self.assertEqual(d("C++"), "programming")
        self.assertEqual(d("Linear Algebra"), "math")
        self.assertEqual(d("Organic Chemistry"), "science")
        self.assertEqual(d("Spanish"), "language")
        self.assertEqual(d("Medieval history"), "generic")

    def test_level_adjustments(self):
        beginner = self.names(self.agent.breakdown(make_req(level="beginner", difficult_topics=[])))
        advanced = self.names(self.agent.breakdown(make_req(level="advanced", difficult_topics=[])))
        inter = self.names(self.agent.breakdown(make_req(level="intermediate", difficult_topics=[])))
        self.assertEqual(beginner[0], FOUNDATIONS)
        self.assertEqual(advanced[0], ADVANCED)
        self.assertNotIn(FOUNDATIONS, inter)
        self.assertEqual(len(advanced), len(inter))

    def test_difficult_topic_matching_existing_topic_is_high(self):
        topics = self.agent.breakdown(make_req(difficult_topics=["error handling"]))
        high = [t["topic"] for t in topics if t["priority"] == "high"]
        self.assertEqual(high, ["Error handling and debugging"])

    def test_unmatched_difficult_topics_are_added_first(self):
        topics = self.agent.breakdown(make_req(difficult_topics=["Metaclasses"]))
        self.assertEqual(topics[0], {"topic": "Metaclasses", "priority": "high"})

    def test_no_duplicates_and_revision_present(self):
        topics = self.names(self.agent.breakdown(make_req(difficult_topics=["Revision and exam practice"])))
        self.assertEqual(len(topics), len({t.lower() for t in topics}))
        self.assertIn(REVISION, topics)

    def test_priorities_are_valid(self):
        for t in self.agent.breakdown(make_req()):
            self.assertIn(t["priority"], ("high", "medium", "low"))

    def test_short_difficult_text_does_not_match_everything(self):
        topics = self.agent.breakdown(make_req(difficult_topics=["a"]))
        self.assertEqual(sum(t["priority"] == "high" for t in topics), 1)


if __name__ == "__main__":
    unittest.main()
