import unittest

from study_planner.agents.collector import RequirementCollector
from study_planner.models import ValidationError
from tests.helpers import TODAY


def scripted(answers):
    it = iter(answers)
    return lambda prompt: next(it)


class CollectorTests(unittest.TestCase):
    def collector(self, **kw):
        return RequirementCollector(output_fn=lambda *_: None, today=TODAY, **kw)

    def test_happy_path(self):
        r = self.collector().collect(scripted(["Python", "Beginner", "2026-12-05", "2", "Recursion, loops", "daily quizzes"]))
        self.assertEqual((r.subject, r.level, r.hours_daily), ("Python", "beginner", 2.0))
        self.assertEqual(r.difficult_topics, ["Recursion", "loops"])
        self.assertEqual(r.start_date, "2026-11-21")

    def test_retries_after_invalid_answers(self):
        r = self.collector().collect(scripted(["", "Math", "expert", "advanced", "2020-01-01", "2026-12-01",
                                               "x", "3", "", "weekly assessments"]))
        self.assertEqual((r.subject, r.level, r.deadline, r.hours_daily), ("Math", "advanced", "2026-12-01", 3.0))
        self.assertEqual(r.difficult_topics, [])

    def test_gives_up_after_max_attempts(self):
        with self.assertRaises(ValidationError):
            self.collector(max_attempts=2).collect(scripted(["", ""]))

    def test_eof_is_reported(self):
        def eof(_):
            raise EOFError
        with self.assertRaises(ValidationError):
            self.collector().collect(eof)

    def test_from_dict(self):
        r = self.collector().from_dict({"subject": "Go", "level": "advanced", "deadline": "2026-12-01", "hours": 1.5})
        self.assertEqual((r.hours_daily, r.assessment), (1.5, "daily quizzes"))

    def test_from_dict_missing_or_wrong_type(self):
        with self.assertRaises(ValidationError):
            self.collector().from_dict({"subject": "Go"})
        with self.assertRaises(ValidationError):
            self.collector().from_dict(["not", "a", "dict"])


if __name__ == "__main__":
    unittest.main()
