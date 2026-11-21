import json
import tempfile
import unittest
from pathlib import Path

from meeting_assistant.cli import main
from tests.helpers import SAMPLE, TODAY


class CliTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.dir = Path(self._tmp.name)
        self.transcript = self.dir / "t.txt"
        self.transcript.write_text(SAMPLE, encoding="utf-8")
        self.out = []

    def run_cli(self, *args, input_fn=input):
        return main(["--output-dir", str(self.dir / "out"), *args], input_fn=input_fn,
                    output_fn=lambda *a: self.out.append(" ".join(map(str, a))), today=TODAY)

    @property
    def text(self):
        return "\n".join(self.out)

    def test_non_interactive_run(self):
        code = self.run_cli("--topic", "Sync", "--attendees", "Maya Rao, Sam Lee", "--transcript-file",
                            str(self.transcript))
        self.assertEqual(code, 0)
        self.assertIn("ACTION ITEMS", self.text)
        saved = json.loads((self.dir / "out" / "meeting_minutes.json").read_text(encoding="utf-8"))
        self.assertEqual(saved["meeting"]["date"], "2026-11-21")
        self.assertEqual(saved["action_items"][0]["owner"], "Sam Lee")  # default: assign when attendees given

    def test_flags_override_defaults(self):
        code = self.run_cli("--topic", "Sync", "--attendees", "Sam", "--transcript-file", str(self.transcript),
                            "--no-assign-tasks", "--no-email", "--detail", "detailed", "--date", "2026-12-01",
                            "--organizer", "Ana")
        self.assertEqual(code, 0)
        out = self.dir / "out"
        saved = json.loads((out / "meeting_minutes.json").read_text(encoding="utf-8"))
        self.assertTrue(all(t["owner"] == "Unassigned" for t in saved["action_items"]))
        self.assertFalse((out / "follow_up_email.md").exists())
        self.assertEqual(saved["meeting"]["organizer"], "Ana")
        self.assertEqual(saved["action_items"][0]["due_date"], "2026-12-04")

    def test_interactive_with_pasted_transcript(self):
        answers = iter(["Sync", "Maya, Sam", "", "short", "", "",
                        "Maya: Sam will send the report tomorrow.", "Sam: Budget approved for design.", "END"])
        self.assertEqual(self.run_cli(input_fn=lambda _: next(answers)), 0)
        self.assertIn("Sam | 2026-11-22", self.text)
        self.assertTrue((self.dir / "out" / "follow_up_email.md").exists())

    def test_interactive_with_file_and_reprompts(self):
        answers = iter(["", "Sync", "Maya", "maybe", "y", "long", "short", "n", str(self.transcript)])
        self.assertEqual(self.run_cli(input_fn=lambda _: next(answers)), 0)
        self.assertIn("! Meeting topic cannot be empty.", self.text)
        self.assertIn("! Please answer yes or no.", self.text)
        self.assertIn("! Summary length must be one of", self.text)
        self.assertFalse((self.dir / "out" / "follow_up_email.md").exists())

    def test_too_many_invalid_answers(self):
        self.assertEqual(self.run_cli(input_fn=lambda _: ""), 1)
        self.assertIn("Error: Too many invalid answers", self.text)

    def test_eof_during_interview(self):
        def eof(_):
            raise EOFError
        self.assertEqual(self.run_cli(input_fn=eof), 1)

    def test_missing_transcript_file(self):
        self.assertEqual(self.run_cli("--topic", "Sync", "--transcript-file", str(self.dir / "nope.txt")), 1)
        self.assertIn("Error:", self.text)

    def test_bad_date_flag(self):
        self.assertEqual(self.run_cli("--topic", "Sync", "--transcript-file", str(self.transcript),
                                      "--date", "tomorrow"), 1)
        self.assertIn("Meeting date", self.text)

    def test_empty_transcript_file(self):
        empty = self.dir / "empty.txt"
        empty.write_text("   \n", encoding="utf-8")
        self.assertEqual(self.run_cli("--topic", "Sync", "--transcript-file", str(empty)), 1)
        self.assertIn("Transcript is empty", self.text)

    def test_log_file_written(self):
        self.run_cli("--topic", "Sync", "--transcript-file", str(self.transcript))
        log = (self.dir / "out" / "log.txt").read_text(encoding="utf-8")
        self.assertIn("Handoff: transcript -> summarizer", log)
        self.assertIn("Meeting minutes saved", log)


if __name__ == "__main__":
    unittest.main()
