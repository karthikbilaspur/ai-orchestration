import unittest

from meeting_assistant.agents.email import FollowUpEmailAgent

TASK = {"task": "Send report", "owner": "Maya", "due_date": "2026-11-27", "due_text": "Friday", "priority": "high"}


class EmailTests(unittest.TestCase):
    agent = FollowUpEmailAgent()

    def test_full_email(self):
        e = self.agent.draft("Sync", "A summary.", [{"text": "Use B"}], [TASK], ["Maya", "Sam"], "Ana", "2026-11-21")
        for part in ("Subject: Follow-up: Sync (2026-11-21)", "To: Maya, Sam", "A summary.", "- Use B",
                     "Owner: Maya | Due: 2026-11-27 | Priority: high", "Best,\nAna"):
            self.assertIn(part, e)

    def test_empty_sections_have_placeholders(self):
        e = self.agent.draft("Sync", "S", [], [])
        self.assertIn("No formal decisions were recorded.", e)
        self.assertIn("No action items were recorded.", e)
        self.assertNotIn("To:", e)
        self.assertTrue(e.endswith("Meeting Organizer"))

    def test_plain_string_decisions_supported(self):
        self.assertIn("- Use B", self.agent.draft("Sync", "S", ["Use B"], []))

    def test_due_text_used_when_no_date(self):
        t = {**TASK, "due_date": None, "due_text": "next month", "priority": "normal"}
        e = self.agent.draft("S", "S", [], [t])
        self.assertIn("Due: next month", e)
        self.assertNotIn("Priority", e)


if __name__ == "__main__":
    unittest.main()
