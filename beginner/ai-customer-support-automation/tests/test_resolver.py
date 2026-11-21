import unittest
from support_system.models import CustomerCase, Classification
from support_system.agents.resolver import ResolverAgent


class ResolverTests(unittest.TestCase):
    def test_technical_steps_are_returned(self):
        case = CustomerCase("App crashes", "today", "major features affected", "no", False)
        result = ResolverAgent().resolve(case, Classification("technical", "medium", "test"))
        self.assertGreaterEqual(len(result.steps), 3)
        self.assertIn("restart", result.steps[0].lower())

    def test_prior_attempt_is_acknowledged(self):
        case = CustomerCase("App crashes", "today", "major features affected", "yes", False)
        result = ResolverAgent().resolve(case, Classification("technical", "medium", "test"))
        self.assertIn("Avoid repeating", result.steps[0])


if __name__ == "__main__":
    unittest.main()
