import unittest

from meeting_assistant.parser import ensure_sentences, parse_transcript, participant_stats, split_sentences


class ParserTests(unittest.TestCase):
    def test_speaker_and_timestamp(self):
        s = parse_transcript("[00:01:23] Maya Rao: We ship Friday. Sam helps.")
        self.assertEqual([x["text"] for x in s], ["We ship Friday.", "Sam helps."])
        self.assertTrue(all(x["speaker"] == "Maya Rao" and x["timestamp"] == "00:01:23" for x in s))
        self.assertEqual([x["index"] for x in s], [0, 1])

    def test_plain_lines_have_no_speaker(self):
        s = parse_transcript("Budget approved. Launch next week.")
        self.assertEqual(len(s), 2)
        self.assertIsNone(s[0]["speaker"])

    def test_labels(self):
        s = parse_transcript("Decision: use option B\nAction item: Alex to send notes\nPriya: Action: Sam to test")
        self.assertEqual([x["label"] for x in s], ["decision", "action item", "action"])
        self.assertEqual(s[0]["text"], "use option B")
        self.assertEqual(s[2]["speaker"], "Priya")

    def test_unknown_single_label_is_not_a_speaker_when_names_known(self):
        s = parse_transcript("Budget: approved by finance", known_names=["Maya"])
        self.assertIsNone(s[0]["speaker"])
        self.assertEqual(s[0]["text"], "Budget: approved by finance")

    def test_repeated_label_counts_as_speaker(self):
        s = parse_transcript("Zed: hi there\nZed: bye now", known_names=["Maya"])
        self.assertEqual(s[0]["speaker"], "Zed")

    def test_first_name_matches_full_name(self):
        s = parse_transcript("Maya: hello team", known_names=["Maya Rao"])
        self.assertEqual(s[0]["speaker"], "Maya")

    def test_abbreviations_do_not_split(self):
        self.assertEqual(len(split_sentences("Ask Dr. Rao about e.g. budgets. Then proceed.")), 2)

    def test_blank_lines_and_bullets_ignored(self):
        s = parse_transcript("\n  \n- Maya: hello world\nSam:\n")
        self.assertEqual(len(s), 1)

    def test_participant_stats(self):
        stats = participant_stats(parse_transcript("A: One two. Three\nB: four\nplain text"))
        self.assertEqual(stats["A"], {"sentences": 2, "words": 3})
        self.assertEqual(stats["B"]["words"], 1)
        self.assertNotIn("plain", stats)

    def test_ensure_sentences_accepts_both(self):
        parsed = parse_transcript("Hello there.")
        self.assertEqual(ensure_sentences(parsed), parsed)
        self.assertEqual(ensure_sentences("Hello there.")[0]["text"], "Hello there.")


if __name__ == "__main__":
    unittest.main()
