import json
import tempfile
import unittest
from datetime import date
from pathlib import Path

from study_planner.models import ValidationError
from study_planner.storage import StorageError
from study_planner.workflow import StudyPlannerWorkflow
from tests.helpers import TODAY, make_req


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.wf = StudyPlannerWorkflow(self._tmp.name, today=TODAY)

    def test_run_writes_plan_and_progress(self):
        report = self.wf.run(make_req(deadline="2026-12-20"))
        plan = json.loads(Path(self._tmp.name, "study_plan.json").read_text(encoding="utf-8"))
        self.assertEqual(plan["summary"]["total_days"], 30)
        self.assertEqual(len(plan["daily_schedule"]), len(report["daily_schedule"]))
        self.assertEqual(report["progress"]["completion_percent"], 0)
        self.assertTrue(Path(self._tmp.name, "progress.json").exists())
        for key in ("requirements", "topic_priorities", "daily_schedule", "practice_questions", "progress"):
            self.assertIn(key, plan)

    def test_mark_done_undo_and_status(self):
        self.wf.run(make_req())
        self.assertEqual(self.wf.mark_done([0, 1])["completed"], 2)
        self.assertEqual(self.wf.status()["completed"], 2)
        self.assertEqual(self.wf.mark_undone([1])["completed_session_indices"], [0])

    def test_out_of_range_session_rejected_and_nothing_saved(self):
        self.wf.run(make_req())
        with self.assertRaises(ValidationError):
            self.wf.mark_done([0, 99])
        self.assertEqual(self.wf.status()["completed"], 0)

    def test_new_plan_resets_progress(self):
        self.wf.run(make_req())
        self.wf.mark_done([0])
        self.wf.run(make_req())
        self.assertEqual(self.wf.status()["completed"], 0)

    def test_missing_plan_raises(self):
        with self.assertRaises(StorageError):
            self.wf.status()

    def test_upcoming_splits_overdue_and_upcoming(self):
        self.wf.run(make_req())
        later = StudyPlannerWorkflow(self._tmp.name, today=date(2026, 11, 24))
        result = later.upcoming(days=3)
        self.assertEqual([s["index"] for s in result["overdue"]], [0, 1, 2])
        self.assertEqual([s["index"] for s in result["upcoming"]], [3, 4, 5])


if __name__ == "__main__":
    unittest.main()
