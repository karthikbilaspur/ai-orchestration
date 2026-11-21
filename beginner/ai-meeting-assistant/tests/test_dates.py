import unittest
from datetime import date

from meeting_assistant.dates import extract_deadline

REF = date(2026, 11, 21)  # Saturday


class DateTests(unittest.TestCase):
    def check(self, text, phrase, iso):
        self.assertEqual(extract_deadline(text, REF), (phrase, iso))

    def test_iso_date(self):
        self.check("Ship by 2026-12-15 please", "2026-12-15", "2026-12-15")

    def test_invalid_iso_falls_through(self):
        self.check("Ship 2026-13-45 tomorrow", "tomorrow", "2026-11-22")

    def test_weekday(self):
        self.check("Send it by Friday", "Friday", "2026-11-27")
        self.check("Send it by Saturday", "Saturday", "2026-11-28")  # same weekday -> next week

    def test_next_weekday_skips_current_week(self):
        self.check("Finish next Monday", "next Monday", "2026-11-23")
        self.assertEqual(extract_deadline("next Friday", date(2026, 11, 23))[1], "2026-12-04")  # Monday: following week
        self.assertEqual(extract_deadline("next Friday", date(2026, 11, 22))[1], "2026-11-27")
        self.assertEqual(extract_deadline("next Friday", date(2026, 11, 20))[1], "2026-11-27")

    def test_relative_phrases(self):
        self.check("do it tomorrow", "tomorrow", "2026-11-22")
        self.check("do it today", "today", "2026-11-21")
        self.check("before next week", "next week", "2026-11-28")
        self.check("by end of the week", "end of the week", "2026-11-27")
        self.check("by end of month", "end of month", "2026-11-30")
        self.check("by EOD", "EOD", "2026-11-21")

    def test_in_n_units(self):
        self.check("in 3 days", "in 3 days", "2026-11-24")
        self.check("in 2 weeks", "in 2 weeks", "2026-12-05")

    def test_next_month_has_phrase_without_date(self):
        self.check("sometime next month", "next month", None)

    def test_no_deadline(self):
        self.check("Update the checklist", None, None)


if __name__ == "__main__":
    unittest.main()
