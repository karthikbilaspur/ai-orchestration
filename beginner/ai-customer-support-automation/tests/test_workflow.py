import json
import tempfile
import unittest
from pathlib import Path
from support_system.models import CustomerCase
from support_system.workflow import CustomerSupportWorkflow


class WorkflowTests(unittest.TestCase):
    def test_agents_handoff_and_report_exports(self):
        case = CustomerCase(
            "I was charged twice for my order", "yesterday",
            "major features affected", "yes", True
        )
        report = CustomerSupportWorkflow().run(case)
        self.assertEqual(report.classification.category, "billing")
        self.assertTrue(report.escalation.required)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "case.json"
            CustomerSupportWorkflow.save_report(report, path)
            saved = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(saved["classification"]["category"], "billing")
            self.assertIn("resolution", saved)


if __name__ == "__main__":
    unittest.main()
