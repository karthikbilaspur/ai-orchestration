import unittest
from support_system.agents.classifier import ClassifierAgent


class ClassifierTests(unittest.TestCase):
    def setUp(self):
        self.agent = ClassifierAgent()

    def test_billing_issue(self):
        result = self.agent.classify("I was charged twice and need a refund for my invoice")
        self.assertEqual(result.category, "billing")
        self.assertEqual(result.confidence, "high")

    def test_unknown_issue(self):
        self.assertEqual(self.agent.classify("I have a question").category, "other")


if __name__ == "__main__":
    unittest.main()
