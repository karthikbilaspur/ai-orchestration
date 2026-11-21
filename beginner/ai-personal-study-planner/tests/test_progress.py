import tempfile
import unittest
from datetime import date
from pathlib import Path

from study_planner.agents.progress import ProgressEvaluator
from tests.helpers import TODAY


def sessions(n=6):
    return [{"index": i, "day": date.fromordinal(TODAY.toordinal() + i).isoformat(),
             "topic": "A" if i % 2 == 0 else "B", "hours": 2.0} for i in range(n)]


class ProgressTests(unittest.TestCase):
    ev = ProgressEvaluator()

    def test_percent_rounds(self):
        self.assertEqual(self.ev.evaluate([{}, {}, {}], [0, 2], TODAY)["completion_percent"], 67)
        self.assertEqual(self.ev.evaluate([], [], TODAY)["completion_percent"], 0)

    def test_invalid_and_duplicate_indices_ignored(self):
        r = self.ev.evaluate(sessions(3), [0, 0, 5, -1, "x"], TODAY)
        self.assertEqual(r["completed_session_indices"], [0])

    def test_status_transitions(self):
        s = sessions(6)
        self.assertEqual(self.ev.evaluate(s, [], date(2026, 11, 20))["status"], "not started")
        self.assertEqual(self.ev.evaluate(s, [0], TODAY)["status"], "on track")
        self.assertEqual(self.ev.evaluate(s, [], date(2026, 11, 22))["status"], "slightly behind")
        self.assertEqual(self.ev.evaluate(s, [], date(2026, 11, 25))["status"], "behind schedule")
        self.assertEqual(self.ev.evaluate(s, range(6), date(2026, 11, 25))["status"], "complete")

    def test_overdue_and_next_session(self):
        r = self.ev.evaluate(sessions(), [0], date(2026, 11, 24))
        self.assertEqual(r["overdue_sessions"], [1, 2])
        self.assertEqual(r["next_session"], 1)
        self.assertIsNone(self.ev.evaluate(sessions(2), [0, 1], TODAY)["next_session"])

    def test_streak(self):
        s = sessions()
        self.assertEqual(self.ev.evaluate(s, [0, 1, 2], date(2026, 11, 23))["streak_days"], 3)
        self.assertEqual(self.ev.evaluate(s, [0, 1], date(2026, 11, 23))["streak_days"], 2)  # today pending
        self.assertEqual(self.ev.evaluate(s, [0, 2], date(2026, 11, 23))["streak_days"], 1)
        self.assertEqual(self.ev.evaluate(s, [], TODAY)["streak_days"], 0)

    def test_hours_and_per_topic(self):
        r = self.ev.evaluate(sessions(), [0, 1, 2], TODAY)
        self.assertEqual((r["hours_completed"], r["hours_total"]), (6.0, 12.0))
        self.assertEqual(r["per_topic"]["A"], {"completed": 2, "total": 3})
        self.assertEqual(r["per_topic"]["B"], {"completed": 1, "total": 3})

    def test_save_and_load_completed(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "progress.json"
            self.assertEqual(self.ev.load_completed(path), [])
            self.ev.save(path, self.ev.evaluate(sessions(), [1, 3], TODAY))
            self.assertEqual(self.ev.load_completed(path), [1, 3])


if __name__ == "__main__":
    unittest.main()
