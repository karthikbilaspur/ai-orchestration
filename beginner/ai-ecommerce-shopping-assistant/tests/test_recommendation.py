import unittest

from shopping_assistant.agents.comparison import ComparisonAgent
from shopping_assistant.agents.product_research import ProductResearchAgent
from shopping_assistant.agents.recommendation import RecommendationAgent, normalize
from shopping_assistant.models import ComparisonTable, Requirements, ResearchResult
from tests.helpers import make_catalog, make_laptop


def pipeline(req, *products):
    research = ProductResearchAgent().run(req, make_catalog(*products))
    table = ComparisonAgent().run(research)
    return RecommendationAgent().run(req, table, research)


class NormalizeTests(unittest.TestCase):
    def test_higher_is_better(self):
        self.assertEqual(normalize([1, 2, 3]), [0.0, 0.5, 1.0])

    def test_lower_is_better(self):
        self.assertEqual(normalize([1, 2, 3], higher_is_better=False), [1.0, 0.5, 0.0])

    def test_all_equal(self):
        self.assertEqual(normalize([4, 4]), [0.5, 0.5])


class RecommendationTests(unittest.TestCase):
    def test_empty_comparison_is_an_error(self):
        with self.assertRaises(ValueError):
            RecommendationAgent().run(Requirements(category="laptop"), ComparisonTable(), ResearchResult())

    def test_better_matching_product_wins(self):
        good = make_laptop("good", "Good", tags=("coding", "travel"))
        meh = make_laptop("meh", "Meh", tags=("coding",))
        rec = pipeline(Requirements(category="laptop", tags=["coding", "travel"]), good, meh)
        self.assertEqual(rec.best.product.id, "good")

    def test_scores_are_between_0_and_1_and_sorted(self):
        rec = pipeline(Requirements(category="laptop"),
                       make_laptop("a", price=500, rating=3.5),
                       make_laptop("b", price=900, rating=4.7),
                       make_laptop("c", price=700, rating=4.1))
        scores = [s.score for s in rec.ranked]
        self.assertTrue(all(0 <= s <= 1 for s in scores))
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_priority_changes_the_winner(self):
        long_battery = make_laptop("long", "Long", price=900, rating=4.0, battery_hours=20)
        cheap = make_laptop("cheap", "Cheap", price=700, rating=4.0, battery_hours=6)
        without = pipeline(Requirements(category="laptop"), long_battery, cheap)
        with_priority = pipeline(Requirements(category="laptop", priorities=["battery"]), long_battery, cheap)
        self.assertEqual(without.best.product.id, "cheap")
        self.assertEqual(with_priority.best.product.id, "long")

    def test_priority_shows_up_in_reasons(self):
        rec = pipeline(Requirements(category="laptop", priorities=["battery"]),
                       make_laptop("long", "Long", battery_hours=20),
                       make_laptop("short", "Short", battery_hours=5))
        self.assertTrue(any("battery" in r.lower() for r in rec.best.reasons))
        self.assertTrue(any("battery" in t.lower() for t in rec.ranked[1].tradeoffs))

    def test_light_priority_prefers_lower_weight(self):
        rec = pipeline(Requirements(category="laptop", priorities=["light"]),
                       make_laptop("heavy", "Heavy", weight_kg=2.4),
                       make_laptop("feather", "Feather", weight_kg=1.0))
        self.assertEqual(rec.best.product.id, "feather")

    def test_inapplicable_priority_is_noted_not_fatal(self):
        rec = pipeline(Requirements(category="laptop", priorities=["camera"]),
                       make_laptop("a"), make_laptop("b", price=900))
        self.assertTrue(any("camera" in n for n in rec.notes))
        self.assertEqual(len(rec.ranked), 2)

    def test_every_product_gets_reasons_or_tradeoffs(self):
        rec = pipeline(Requirements(category="laptop", max_budget=1000, tags=["coding"]),
                       make_laptop("a", price=600), make_laptop("b", price=950, rating=4.7))
        for s in rec.ranked:
            self.assertTrue(s.reasons or s.tradeoffs)
            self.assertTrue(s.tradeoffs)       # never empty: falls back to a friendly line

    def test_over_budget_is_called_out(self):
        req = Requirements(category="laptop", max_budget=500, tags=["coding"])
        research = ProductResearchAgent().run(req, make_catalog(make_laptop("a", price=540)))
        table = ComparisonAgent().run(research)
        rec = RecommendationAgent().run(req, table, research)
        self.assertTrue(any("Over your budget" in t for t in rec.best.tradeoffs))
        self.assertTrue(any("stretched" in n for n in rec.notes))

    def test_explanation_names_both_products(self):
        rec = pipeline(Requirements(category="laptop", tags=["coding", "travel"]),
                       make_laptop("a", "Alpha", tags=("coding", "travel")),
                       make_laptop("b", "Beta", tags=("coding",)))
        self.assertIn("Alpha", rec.explanation)
        self.assertIn("Beta", rec.explanation)

    def test_single_product_explanation(self):
        rec = pipeline(Requirements(category="laptop"), make_laptop("only", "Solo"))
        self.assertIn("only product", rec.explanation)

    def test_no_match_at_all_is_flagged(self):
        rec = pipeline(Requirements(category="laptop", tags=["gaming"]), make_laptop("a", tags=("office",)))
        self.assertTrue(any("closest option" in n for n in rec.notes))

    def test_weights_sum_to_one(self):
        rec = pipeline(Requirements(category="laptop", tags=["coding"], priorities=["battery"]),
                       make_laptop("a"), make_laptop("b", battery_hours=12))
        self.assertAlmostEqual(sum(rec.weights_used.values()), 1.0, places=2)
        self.assertEqual(set(rec.weights_used), {"fit", "quality", "value", "priority"})

    def test_fit_weight_dropped_without_needs(self):
        rec = pipeline(Requirements(category="laptop"), make_laptop("a"), make_laptop("b", price=900))
        self.assertNotIn("fit", rec.weights_used)

    def test_deterministic(self):
        req = Requirements(category="laptop", tags=["coding"], priorities=["battery"])
        products = [make_laptop("a", price=700), make_laptop("b", price=900, battery_hours=14)]
        first = pipeline(req, *products)
        second = pipeline(req, *products)
        self.assertEqual([s.product.id for s in first.ranked], [s.product.id for s in second.ranked])
        self.assertEqual([s.score for s in first.ranked], [s.score for s in second.ranked])


if __name__ == "__main__":
    unittest.main()
