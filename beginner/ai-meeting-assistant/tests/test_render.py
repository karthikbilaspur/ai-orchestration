import tempfile
import unittest

from meeting_assistant.render import render_console, render_minutes_markdown
from meeting_assistant.workflow import MeetingWorkflow
from tests.helpers import make_meeting


class RenderTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.report = MeetingWorkflow(tmp.name).run(make_meeting())

    def test_markdown_sections(self):
        md = render_minutes_markdown(self.report)
        for part in ("# Meeting Minutes: Q4 Launch Sync", "## Summary", "## Decisions", "## Action items",
                     "| A1 |", "## Participation"):
            self.assertIn(part, md)

    def test_pipes_in_tasks_are_escaped(self):
        self.report["action_items"][0]["task"] = "a | b"
        self.assertIn("a \\| b", render_minutes_markdown(self.report))

    def test_empty_report_placeholders(self):
        self.report.update(decisions=[], action_items=[], key_topics=[], participants={}, warnings=[])
        md = render_minutes_markdown(self.report)
        self.assertEqual(md.count("_None detected._"), 2)
        self.assertNotIn("## Key topics", md)
        console = render_console(self.report)
        self.assertIn("(none detected)", console)

    def test_console_lists_files(self):
        self.assertIn("meeting_minutes.json", render_console(self.report))


if __name__ == "__main__":
    unittest.main()
