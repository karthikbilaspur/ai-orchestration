import unittest

from study_planner.agents.quiz import QuizGenerator
from tests.test_schedule import build


class QuizTests(unittest.TestCase):
    def test_daily_quizzes_cover_every_study_session(self):
        req, _, s = build(deadline="2026-12-20")
        qs = QuizGenerator().generate(req, s)
        study = [x for x in s if x["kind"] == "study"]
        self.assertGreaterEqual(len(qs), len(study))
        self.assertTrue(all(q["topic"] in q["question"] for q in qs))
        self.assertEqual({q["kind"] for q in qs}, {"daily quiz", "revision check"})

    def test_weekly_mode_has_no_daily_questions(self):
        req, _, s = build(deadline="2026-12-20", assessment="weekly assessments")
        qs = QuizGenerator().generate(req, s)
        self.assertNotIn("daily quiz", {q["kind"] for q in qs})
        self.assertIn("weekly assessment", {q["kind"] for q in qs})
        valid = {x["index"] for x in s if x["kind"] != "study"}
        self.assertTrue({q["session_index"] for q in qs} <= valid)

    def test_question_templates_vary(self):
        req, _, s = build(deadline="2026-12-20")
        qs = QuizGenerator().generate(req, s)
        self.assertGreater(len({q["question"].split()[0] for q in qs}), 2)


if __name__ == "__main__":
    unittest.main()
