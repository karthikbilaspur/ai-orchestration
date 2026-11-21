import unittest

from study_planner.models import MAX_PLAN_DAYS, StudyRequirements, ValidationError, parse_topics
from tests.helpers import make_req


class ModelTests(unittest.TestCase):
    def test_normalizes_values(self):
        r = make_req(subject="  Data   Science ", level=" Beginner ", assessment="Daily  Quizzes")
        self.assertEqual((r.subject, r.level, r.assessment), ("Data Science", "beginner", "daily quizzes"))

    def test_days_available_is_inclusive(self):
        self.assertEqual(make_req().days_available, 15)
        self.assertEqual(make_req(deadline="2026-11-21").days_available, 1)

    def test_rejects_bad_inputs(self):
        for kw in ({"subject": "   "}, {"subject": "x" * 101}, {"level": "expert"},
                   {"hours_daily": "abc"}, {"hours_daily": 0}, {"hours_daily": 17},
                   {"hours_daily": float("nan")}, {"assessment": "never"},
                   {"deadline": "05-12-2026"}, {"deadline": "2026-11-20"}, {"start_date": "nope"}):
            with self.subTest(kw=kw), self.assertRaises(ValidationError):
                make_req(**kw)

    def test_rejects_far_deadline(self):
        with self.assertRaises(ValidationError):
            make_req(deadline="2099-01-01")
        self.assertLessEqual(make_req(deadline="2027-11-21").days_available, MAX_PLAN_DAYS)

    def test_parse_topics_dedupes_and_splits(self):
        self.assertEqual(parse_topics("a, B ,a,, b"), ["a", "B"])
        self.assertEqual(parse_topics(None), [])
        self.assertEqual(parse_topics(["x", " x ", "y"]), ["x", "y"])

    def test_to_dict_round_trip(self):
        r = make_req()
        self.assertEqual(StudyRequirements(**r.to_dict()).to_dict(), r.to_dict())


if __name__ == "__main__":
    unittest.main()
