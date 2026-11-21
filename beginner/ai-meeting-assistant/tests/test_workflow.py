import json
import tempfile
import unittest
from pathlib import Path

from meeting_assistant.models import ValidationError
from meeting_assistant.workflow import MeetingWorkflow
from tests.helpers import make_meeting


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.dir = Path(self._tmp.name)

    def test_run_writes_all_outputs(self):
        report = MeetingWorkflow(self.dir).run(make_meeting())
        self.assertEqual(sorted(p.name for p in self.dir.iterdir()),
                         ["follow_up_email.md", "meeting_minutes.json", "meeting_minutes.md"])
        saved = json.loads((self.dir / "meeting_minutes.json").read_text(encoding="utf-8"))
        self.assertEqual(saved["stats"], report["stats"])
        self.assertEqual(report["stats"]["decisions"], 2)
        self.assertEqual(report["stats"]["action_items"], 5)
        self.assertIn("follow_up_email", saved)

    def test_no_email_when_disabled(self):
        report = MeetingWorkflow(self.dir).run(make_meeting(make_email=False))
        self.assertNotIn("follow_up_email", report)
        self.assertFalse((self.dir / "follow_up_email.md").exists())
        self.assertNotIn("follow_up_email.md", report["output_files"])

    def test_assign_false_keeps_tasks_unassigned(self):
        report = MeetingWorkflow(self.dir).run(make_meeting(assign_tasks=False))
        self.assertTrue(all(t["owner"] == "Unassigned" for t in report["action_items"]))

    def test_warnings(self):
        r = MeetingWorkflow(self.dir).run(make_meeting(transcript="We chatted about lunch options today.",
                                                       attendees=[], assign_tasks=True))
        text = " ".join(r["warnings"])
        for part in ("No speaker labels", "no attendees", "No decisions", "No action items"):
            self.assertIn(part.lower(), text.lower())

    def test_unlisted_speaker_warning(self):
        r = MeetingWorkflow(self.dir).run(make_meeting(transcript="Zoe: hello team\nZoe: bye team", attendees=["Maya"]))
        self.assertTrue(any("Zoe" in w for w in r["warnings"]))

    def test_unparseable_transcript_rejected(self):
        with self.assertRaises(ValidationError):
            MeetingWorkflow(self.dir).run(make_meeting(transcript="Maya:"))

    def test_creates_output_directory(self):
        target = self.dir / "nested" / "out"
        MeetingWorkflow(target).run(make_meeting())
        self.assertTrue((target / "meeting_minutes.json").exists())

    def test_detailed_summary_is_bulleted(self):
        report = MeetingWorkflow(self.dir).run(make_meeting(detail="detailed"))
        self.assertTrue(report["summary"].startswith("- "))


if __name__ == "__main__":
    unittest.main()
