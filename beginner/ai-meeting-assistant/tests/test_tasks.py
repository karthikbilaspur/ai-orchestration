import unittest
from datetime import date

from meeting_assistant.agents.tasks import TaskAssignmentAgent
from tests.helpers import ATTENDEES, SAMPLE, TODAY


class TaskTests(unittest.TestCase):
    agent = TaskAssignmentAgent()

    def extract(self, text, attendees=ATTENDEES, assign=True):
        return self.agent.extract(text, attendees, assign, TODAY)

    def test_named_owner(self):
        r = self.agent.extract("Maya will send the report", ["Maya"], True)
        self.assertEqual(r[0]["owner"], "Maya")

    def test_full_name_resolution_from_first_name(self):
        self.assertEqual(self.extract("Sam will fix the bug")[0]["owner"], "Sam Lee")

    def test_first_person_uses_speaker(self):
        r = self.extract("Priya: I will update the checklist tomorrow.")
        self.assertEqual((r[0]["owner"], r[0]["due_date"]), ("Priya", "2026-11-22"))
        self.assertEqual(self.extract("Priya: I'll update the checklist.")[0]["owner"], "Priya")

    def test_first_person_without_speaker_is_unassigned(self):
        self.assertEqual(self.extract("I will update the checklist.")[0]["owner"], "Unassigned")

    def test_multiple_owners_and_group(self):
        self.assertEqual(self.extract("Maya and Sam will pair on the demo.")[0]["owner"], "Maya Rao & Sam Lee")
        self.assertEqual(self.extract("We need to revisit pricing.")[0]["owner"], "Team")

    def test_assign_false_leaves_unassigned(self):
        self.assertEqual(self.extract("Sam will fix the bug", assign=False)[0]["owner"], "Unassigned")

    def test_request_assigns_addressee(self):
        r = self.extract("Sam: Maya, can you approve the budget before next week?")
        self.assertEqual((r[0]["owner"], r[0]["source"], r[0]["due_date"]), ("Maya Rao", "request", "2026-11-28"))

    def test_other_questions_are_not_tasks(self):
        self.assertEqual(self.extract("Who will handle the budget?"), [])

    def test_labelled_action_with_unlisted_owner(self):
        r = self.extract("Action: Alex to prepare the announcement ASAP.")
        self.assertEqual((r[0]["owner"], r[0]["priority"], r[0]["source"]), ("Alex", "high", "label"))

    def test_labelled_action_without_owner(self):
        self.assertEqual(self.extract("TODO: update the roadmap")[0]["owner"], "Unassigned")

    def test_will_be_is_not_a_task(self):
        self.assertEqual(self.extract("The launch will be great and Sam will be there."), [])

    def test_priority_levels(self):
        self.assertEqual(self.extract("Sam must fix the urgent bug")[0]["priority"], "high")
        self.assertEqual(self.extract("Sam will tidy docs when possible")[0]["priority"], "low")
        self.assertEqual(self.extract("Sam will fix the bug")[0]["priority"], "normal")

    def test_deadline_resolved_from_reference_date(self):
        r = self.agent.extract("Sam will redesign it by Friday", ["Sam"], True, date(2026, 11, 23))
        self.assertEqual(r[0]["due_date"], "2026-11-27")

    def test_ids_and_dedupe(self):
        r = self.extract("Sam will fix A.\nSam will fix A.\nMaya will fix B.")
        self.assertEqual([t["id"] for t in r], ["A1", "A2"])

    def test_ambiguous_first_names_are_not_resolved(self):
        r = self.agent.extract("Sam will fix it", ["Sam Lee", "Sam Cho"], True, TODAY)
        self.assertEqual(r[0]["owner"], "Unassigned")

    def test_sample_transcript(self):
        r = self.extract(SAMPLE)
        self.assertEqual([t["owner"] for t in r], ["Sam Lee", "Priya", "Maya Rao", "Alex", "Team"])
        self.assertEqual(r[3]["priority"], "high")


if __name__ == "__main__":
    unittest.main()
