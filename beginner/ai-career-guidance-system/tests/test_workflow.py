import json
import tempfile
import unittest
from pathlib import Path

from career_guidance.models import LearnerProfile
from career_guidance.workflow import CareerGuidanceWorkflow


class WorkflowTests(unittest.TestCase):
    def test_full_handoff_and_json_export(self):
        profile = LearnerProfile("B.Tech", ["python"], ["ai"], 2, "balanced", "internship")
        workflow = CareerGuidanceWorkflow()
        report = workflow.run(profile)
        self.assertEqual(report.career_recommendations[0].career, "AI / Machine Learning Engineer")
        self.assertEqual(len(report.roadmap), 7)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "report.json"
            workflow.save_report(report, str(path))
            data = json.loads(path.read_text(encoding="utf-8"))
            self.assertIn("skill_analysis", data)
            self.assertEqual(len(data["roadmap"]), 7)


if __name__ == "__main__":
    unittest.main()
