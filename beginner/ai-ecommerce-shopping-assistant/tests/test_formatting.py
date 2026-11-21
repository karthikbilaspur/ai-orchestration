import unittest

from shopping_assistant.agents.comparison import ComparisonAgent
from shopping_assistant.formatting import format_value, render_comparison
from shopping_assistant.models import Candidate, ComparisonTable, ResearchResult
from tests.helpers import make_laptop


class FormatValueTests(unittest.TestCase):
    def test_price(self):
        self.assertEqual(format_value("price", "num", "$", 1099), "$1,099")

    def test_rating(self):
        self.assertEqual(format_value("rating", "num", "/5", 4.5), "4.5/5")

    def test_bool(self):
        self.assertEqual(format_value("x", "bool", "", 1), "Yes")
        self.assertEqual(format_value("x", "bool", "", 0), "No")

    def test_numbers_with_units(self):
        self.assertEqual(format_value("ram_gb", "num", "GB", 16.0), "16 GB")
        self.assertEqual(format_value("weight_kg", "num", "kg", 1.24), "1.24 kg")
        self.assertEqual(format_value("cushion", "num", "/5", 4), "4/5")


class RenderComparisonTests(unittest.TestCase):
    def test_table_contains_names_and_best_markers(self):
        research = ResearchResult(candidates=[Candidate(make_laptop("a", "Alpha", price=500), 1),
                                              Candidate(make_laptop("b", "Beta", price=900), 1)])
        text = render_comparison(ComparisonAgent().run(research))
        self.assertIn("Alpha", text)
        self.assertIn("Beta", text)
        self.assertIn("$500 *", text)
        self.assertIn("best value", text)

    def test_empty_table(self):
        self.assertIn("nothing", render_comparison(ComparisonTable()).lower())


if __name__ == "__main__":
    unittest.main()
