import json
import tempfile
import unittest
from pathlib import Path

from study_planner.cli import main
from tests.helpers import TODAY

FLAGS = ["--subject", "Python", "--level", "beginner", "--deadline", "2026-12-05",
         "--hours", "2", "--assessment", "daily quizzes"]


class CliTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.out = []

    def run_cli(self, *args, input_fn=input):
        return main(["--data-dir", self._tmp.name, *args], input_fn=input_fn,
                    output_fn=lambda *a: self.out.append(" ".join(map(str, a))), today=TODAY)

    @property
    def text(self):
        return "\n".join(self.out)

    def test_plan_from_flags_then_progress_commands(self):
        self.assertEqual(self.run_cli("plan", *FLAGS), 0)
        self.assertIn("TOPIC PRIORITIES", self.text)
        self.assertIn("PRACTICE QUESTIONS", self.text)
        self.out.clear()
        self.assertEqual(self.run_cli("done", "0", "1"), 0)
        self.assertIn("2/15 sessions", self.text)
        self.out.clear()
        self.assertEqual(self.run_cli("status"), 0)
        self.assertIn("Streak", self.text)
        self.out.clear()
        self.assertEqual(self.run_cli("undo", "1"), 0)
        self.assertIn("1/15", self.text)
        self.out.clear()
        self.assertEqual(self.run_cli("show", "--days", "3"), 0)
        self.assertIn("UPCOMING", self.text)

    def test_plan_from_json_file(self):
        f = Path(self._tmp.name, "req.json")
        f.write_text(json.dumps({"subject": "Algebra", "level": "intermediate", "deadline": "2026-11-30",
                                 "hours_daily": 1, "assessment": "weekly assessments"}), encoding="utf-8")
        self.assertEqual(self.run_cli("plan", "--from-json", str(f)), 0)
        self.assertIn("Definitions and notation", self.text)

    def test_interactive_plan_is_default_command(self):
        answers = iter(["Physics", "advanced", "2026-12-01", "1.5", "Optics", "daily quizzes"])
        self.assertEqual(self.run_cli(input_fn=lambda _: next(answers)), 0)
        self.assertIn("Optics: high", self.text)

    def test_partial_flags_return_error(self):
        self.assertEqual(self.run_cli("plan", "--subject", "Python"), 1)
        self.assertIn("Missing flag", self.text)

    def test_invalid_input_returns_error_code(self):
        bad = FLAGS.copy()
        bad[bad.index("2026-12-05")] = "2020-01-01"
        self.assertEqual(self.run_cli("plan", *bad), 1)
        self.assertIn("Deadline", self.text)

    def test_bad_json_file(self):
        f = Path(self._tmp.name, "bad.json")
        f.write_text("{", encoding="utf-8")
        self.assertEqual(self.run_cli("plan", "--from-json", str(f)), 1)

    def test_commands_without_plan_fail_cleanly(self):
        self.assertEqual(self.run_cli("status"), 1)
        self.assertIn("No study plan", self.text)

    def test_log_file_is_written(self):
        self.run_cli("plan", *FLAGS)
        log = Path(self._tmp.name, "log.txt").read_text(encoding="utf-8")
        self.assertIn("Handoff: collector -> topic breakdown", log)
        self.assertIn("Plan saved", log)


if __name__ == "__main__":
    unittest.main()
