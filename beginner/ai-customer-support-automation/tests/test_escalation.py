import unittest
from support_system.models import CustomerCase, Classification, Priority, Resolution
from support_system.agents.escalation import EscalationAgent


class EscalationTests(unittest.TestCase):
    def test_customer_request_triggers_handoff(self):
        case = CustomerCase("Need help with an order", "today", "minor inconvenience", "no", True)
        result = EscalationAgent().decide(
            case, Classification("delivery", "medium", ""),
            Priority("low", 1, ""), Resolution("", [])
        )
        self.assertTrue(result.required)
        self.assertEqual(result.handoff_queue, "Order and Delivery Support")

    def test_no_trigger_stays_self_service(self):
        case = CustomerCase("How do I change a setting?", "today", "no impact", "no", False)
        result = EscalationAgent().decide(
            case, Classification("other", "low", ""),
            Priority("low", 0, ""), Resolution("", [])
        )
        self.assertFalse(result.required)


if __name__ == "__main__":
    unittest.main()
