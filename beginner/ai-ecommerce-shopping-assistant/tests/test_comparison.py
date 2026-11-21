import unittest

from shopping_assistant.agents.comparison import ComparisonAgent
from shopping_assistant.models import Candidate, ResearchResult
from tests.helpers import make_laptop


def research_of(*products):
    return ResearchResult(candidates=[Candidate(p, 1.0) for p in products])


class ComparisonTests(unittest.TestCase):
    def setUp(self):
        self.cheap = make_laptop("a", "Cheap", price=500, rating=3.8, battery_hours=8, weight_kg=2.0)
        self.fancy = make_laptop("b", "Fancy", price=1500, rating=4.8, battery_hours=16, weight_kg=1.1)
        self.table = ComparisonAgent().run(research_of(self.cheap, self.fancy))

    def test_rows_include_price_rating_and_specs(self):
        keys = [r.key for r in self.table.rows]
        self.assertEqual(keys[:2], ["price", "rating"])
        for spec in ("ram_gb", "storage_gb", "battery_hours", "weight_kg"):
            self.assertIn(spec, keys)

    def test_lower_price_is_best(self):
        self.assertEqual(self.table.row("price").best_ids, ["a"])
        self.assertEqual(self.table.row("price").worst_ids, ["b"])

    def test_higher_rating_and_battery_are_best(self):
        self.assertEqual(self.table.row("rating").best_ids, ["b"])
        self.assertEqual(self.table.row("battery_hours").best_ids, ["b"])

    def test_lower_weight_is_best(self):
        self.assertEqual(self.table.row("weight_kg").best_ids, ["b"])

    def test_ties_have_no_winner(self):
        self.assertEqual(self.table.row("ram_gb").best_ids, [])
        self.assertEqual(self.table.row("ram_gb").worst_ids, [])

    def test_two_way_tie_for_best(self):
        a = make_laptop("a", ram_gb=32)
        b = make_laptop("b", ram_gb=32)
        c = make_laptop("c", ram_gb=8)
        table = ComparisonAgent().run(research_of(a, b, c))
        self.assertEqual(sorted(table.row("ram_gb").best_ids), ["a", "b"])
        self.assertEqual(table.row("ram_gb").worst_ids, ["c"])

    def test_top_n_limit(self):
        many = [make_laptop(str(i), f"L{i}", price=500 + i) for i in range(6)]
        self.assertEqual(len(ComparisonAgent(top_n=3).run(research_of(*many)).products), 3)

    def test_empty_input(self):
        table = ComparisonAgent().run(ResearchResult())
        self.assertEqual(table.products, [])
        self.assertEqual(table.rows, [])

    def test_single_product_has_no_winners(self):
        table = ComparisonAgent().run(research_of(self.cheap))
        self.assertTrue(all(r.best_ids == [] for r in table.rows))

    def test_row_lookup_missing(self):
        self.assertIsNone(self.table.row("does_not_exist"))


if __name__ == "__main__":
    unittest.main()
