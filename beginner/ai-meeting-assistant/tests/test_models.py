import unittest

from meeting_assistant.models import (
    MAX_TRANSCRIPT_CHARS, MeetingInput, ValidationError, parse_attendees, parse_bool, validate_detail,
)
from tests.helpers import make_meeting


class ModelTests(unittest.TestCase):
    def test_normalizes_fields(self):
        m = make_meeting(topic="  Q4   sync ", detail=" DETAILED ", organizer="  Ana  Ruiz ")
        self.assertEqual((m.topic, m.detail, m.organizer), ("Q4 sync", "detailed", "Ana Ruiz"))

    def test_line_endings_and_whitespace(self):
        self.assertEqual(MeetingInput("T", "  a\r\nb  ").transcript, "a\nb")

    def test_rejects_bad_input(self):
        for kw in ({"topic": " "}, {"topic": "x" * 121}, {"transcript": "  \n "}, {"detail": "long"},
                   {"meeting_date": "21-11-2026"}, {"transcript": "x" * (MAX_TRANSCRIPT_CHARS + 1)}):
            with self.subTest(kw=kw), self.assertRaises(ValidationError):
                make_meeting(**kw)

    def test_blank_detail_defaults_to_short(self):
        self.assertEqual(validate_detail("  "), "short")

    def test_parse_attendees(self):
        self.assertEqual(parse_attendees("Maya, sam ,Maya,\nSam,, Priya"), ["Maya", "sam", "Priya"])
        self.assertEqual(parse_attendees(None), [])
        self.assertEqual(parse_attendees(["A", " a ", "B"]), ["A", "B"])

    def test_parse_bool(self):
        self.assertTrue(parse_bool("Yes"))
        self.assertFalse(parse_bool("n"))
        self.assertTrue(parse_bool("", default=True))
        with self.assertRaises(ValidationError):
            parse_bool("maybe")
        with self.assertRaises(ValidationError):
            parse_bool("")

    def test_reference_date(self):
        self.assertEqual(make_meeting().reference_date.isoformat(), "2026-11-21")


if __name__ == "__main__":
    unittest.main()
