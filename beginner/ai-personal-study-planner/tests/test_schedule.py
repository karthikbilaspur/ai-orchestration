import unittest
from collections import Counter
from datetime import date, timedelta

from study_planner.agents.schedule import PHASES, ScheduleGenerator, weighted_sequence
from study_planner.agents.topic_breakdown import TopicBreakdownAgent
from tests.helpers import make_req


def build(**kw):
    req = make_req(**kw)
    topics = TopicBreakdownAgent().breakdown(req)
    return req, topics, ScheduleGenerator().generate(req, topics)


class ScheduleTests(unittest.TestCase):
    def test_one_session_per_day_contiguous(self):
        req, _, s = build()
        self.assertEqual(len(s), req.days_available)
        for i, session in enumerate(s):
            self.assertEqual(session["index"], i)
            self.assertEqual(session["day"], (date(2026, 11, 21) + timedelta(days=i)).isoformat())
            self.assertEqual(session["hours"], 2.0)

    def test_revision_at_end_for_longer_plans(self):
        _, _, s = build(deadline="2026-12-20")  # 30 days -> 3 revision days
        self.assertEqual([x["kind"] for x in s[-3:]], ["revision"] * 3)
        self.assertEqual(sum(x["kind"] == "revision" for x in s), 3)

    def test_no_revision_for_short_plans(self):
        _, _, s = build(deadline="2026-11-24")
        self.assertTrue(all(x["kind"] == "study" for x in s))

    def test_single_day_plan(self):
        _, _, s = build(deadline="2026-11-21")
        self.assertEqual(len(s), 1)
        self.assertEqual(s[0]["kind"], "study")

    def test_weekly_assessments_every_seventh_day(self):
        _, _, s = build(deadline="2026-12-20", assessment="weekly assessments")
        days = [x["index"] for x in s if x["kind"] == "assessment"]
        self.assertEqual(days, [6, 13, 20, 27][:len(days)])
        self.assertTrue(days)
        self.assertTrue(all(x["covers"] for x in s if x["kind"] == "assessment"))

    def test_daily_quizzes_have_no_assessment_days(self):
        _, _, s = build(deadline="2026-12-20")
        self.assertFalse(any(x["kind"] == "assessment" for x in s))

    def test_high_priority_gets_more_sessions_than_low(self):
        _, _, s = build(deadline="2026-12-20")
        counts = Counter(x["topic"] for x in s if x["kind"] == "study")
        self.assertGreater(counts["Error handling and debugging"], counts["Projects and practice problems"])

    def test_activity_phases_rotate_per_topic(self):
        _, _, s = build(deadline="2026-12-20")
        mine = [x["activity"] for x in s if x["topic"] == "Error handling and debugging"]
        self.assertEqual(mine[:3], list(PHASES))

    def test_weighted_sequence_proportions_and_determinism(self):
        topics = [{"topic": "A", "priority": "high"}, {"topic": "B", "priority": "low"}]
        seq = [t["topic"] for t in weighted_sequence(topics, 8)]
        self.assertEqual(Counter(seq), {"A": 6, "B": 2})
        self.assertEqual(seq, [t["topic"] for t in weighted_sequence(topics, 8)])

    def test_empty_topics_rejected(self):
        with self.assertRaises(ValueError):
            ScheduleGenerator().generate(make_req(), [])


if __name__ == "__main__":
    unittest.main()
