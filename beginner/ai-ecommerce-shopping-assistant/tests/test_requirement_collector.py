import unittest

from shopping_assistant.agents.requirement_collector import (
    RequirementCollectorAgent, detect_category, parse_budget, parse_min_specs)
from tests.helpers import scripted


class CategoryTests(unittest.TestCase):
    def test_basic_categories(self):
        self.assertEqual(detect_category("I want a Laptop"), "laptop")
        self.assertEqual(detect_category("good running shoes"), "running_shoes")
        self.assertEqual(detect_category("a new smartphone"), "smartphone")

    def test_headphones_are_not_phones(self):
        self.assertEqual(detect_category("studio headphones"), "headphones")

    def test_last_category_wins(self):
        self.assertEqual(detect_category("a laptop bag"), "backpack")

    def test_unknown(self):
        self.assertIsNone(detect_category("something nice"))


class BudgetTests(unittest.TestCase):
    def test_under(self):
        self.assertEqual(parse_budget("laptop under 1000"), (None, 1000.0))

    def test_dollar_and_commas(self):
        self.assertEqual(parse_budget("below $1,200 please"), (None, 1200.0))

    def test_k_suffix(self):
        self.assertEqual(parse_budget("budget of 1.5k"), (None, 1500.0))

    def test_between(self):
        self.assertEqual(parse_budget("between 500 and 800"), (500.0, 800.0))

    def test_min_needs_dollar_sign(self):
        self.assertEqual(parse_budget("at least $300 and under $600"), (300.0, 600.0))

    def test_bare_dollar_amount_is_a_max(self):
        self.assertEqual(parse_budget("a phone for $400"), (None, 400.0))

    def test_specs_are_not_budgets(self):
        self.assertEqual(parse_budget("under 1.5 kg"), (None, None))
        self.assertEqual(parse_budget("at most 16gb ram"), (None, None))
        self.assertEqual(parse_budget("about 10 hours of battery"), (None, None))

    def test_no_budget(self):
        self.assertEqual(parse_budget("just a laptop"), (None, None))


class MinSpecTests(unittest.TestCase):
    def test_ram_storage_battery(self):
        specs = parse_min_specs("16GB RAM, 1TB SSD and 12 hours battery")
        self.assertEqual(specs, {"ram_gb": 16.0, "storage_gb": 1000.0, "battery_hours": 12.0})

    def test_none(self):
        self.assertEqual(parse_min_specs("a nice laptop"), {})


class ParseTests(unittest.TestCase):
    def setUp(self):
        self.agent = RequirementCollectorAgent(known_brands=["Nimbus", "Vertex"])

    def test_full_request(self):
        req = self.agent.parse("I need a laptop under 1000 for coding and travel, lightweight with good battery")
        self.assertEqual(req.category, "laptop")
        self.assertEqual(req.max_budget, 1000.0)
        self.assertEqual(req.tags, ["coding", "travel"])
        self.assertEqual(req.priorities, ["light", "battery"])

    def test_priorities_keep_spoken_order(self):
        req = self.agent.parse("laptop with great battery and lightweight")
        self.assertEqual(req.priorities, ["battery", "light"])

    def test_brand_detection_is_case_insensitive(self):
        req = self.agent.parse("a nimbus laptop")
        self.assertEqual(req.brands, ["Nimbus"])

    def test_no_false_brand(self):
        self.assertEqual(self.agent.parse("a laptop").brands, [])

    def test_multiword_tag(self):
        req = self.agent.parse("noise cancelling headphones")
        self.assertIn("noise-cancelling", req.tags)

    def test_summary_text(self):
        req = self.agent.parse("laptop under 900 for coding")
        text = req.summary()
        self.assertIn("laptop", text)
        self.assertIn("$900", text)
        self.assertIn("coding", text)

    def test_missing_fields(self):
        self.assertEqual(self.agent.parse("hello").missing_fields(), ["category"])
        self.assertEqual(self.agent.parse("laptop").missing_fields(), [])


class FollowUpTests(unittest.TestCase):
    def setUp(self):
        self.agent = RequirementCollectorAgent()

    def test_no_questions_without_input_fn(self):
        req = self.agent.run("something nice")
        self.assertIsNone(req.category)

    def test_asks_for_category_budget_and_needs(self):
        ask = scripted(["backpack", "under $100", "hiking and travel"])
        req = self.agent.run("help me", input_fn=ask)
        self.assertEqual(req.category, "backpack")
        self.assertEqual(req.max_budget, 100.0)
        self.assertEqual(set(req.tags), {"hiking", "travel"})
        self.assertEqual(len(ask.prompts), 3)

    def test_bare_number_budget_answer(self):
        req = self.agent.run("a laptop", input_fn=scripted(["900", ""]))
        self.assertEqual(req.max_budget, 900.0)

    def test_does_not_ask_what_it_already_knows(self):
        ask = scripted([])
        self.agent.run("laptop under 900 for coding", input_fn=ask)
        self.assertEqual(ask.prompts, [])

    def test_gives_up_after_two_bad_category_answers(self):
        ask = scripted(["???", "still nothing"])
        req = self.agent.run("help", input_fn=ask)
        self.assertIsNone(req.category)
        self.assertEqual(len(ask.prompts), 2)

    def test_blank_answer_skips(self):
        ask = scripted([""])
        req = self.agent.run("help", input_fn=ask)
        self.assertIsNone(req.category)
        self.assertEqual(len(ask.prompts), 1)

    def test_eof_is_treated_as_blank(self):
        def broken(prompt):
            raise EOFError
        req = self.agent.run("laptop", input_fn=broken)
        self.assertEqual(req.category, "laptop")


if __name__ == "__main__":
    unittest.main()
