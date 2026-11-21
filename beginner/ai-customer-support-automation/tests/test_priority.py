import unittest
from support_system.models import CustomerCase, Classification
from support_system.agents.priority import PriorityAgent


class PriorityTests(unittest.TestCase):
    def test_cannot_use_product_is_high(self):
        case = CustomerCase("The app is down", "today", "cannot use product", "no", False)
        result = PriorityAgent().assess(case, Classification("technical", "medium", "test"))
        self.assertEqual(result.level, "high")

    def test_minor_issue_is_low(self):
        case = CustomerCase("Small display issue", "today", "minor inconvenience", "no", False)
        result = PriorityAgent().assess(case, Classification("technical", "medium", "test"))
        self.assertEqual(result.level, "low")


if __name__ == "__main__":
    unittest.main()
