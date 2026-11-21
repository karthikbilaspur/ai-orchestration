import unittest

from shopping_assistant.agents.product_research import ProductResearchAgent
from shopping_assistant.catalog import load_default_catalog
from shopping_assistant.models import Requirements
from tests.helpers import make_catalog, make_laptop


class ResearchTests(unittest.TestCase):
    def setUp(self):
        self.catalog = load_default_catalog()
        self.agent = ProductResearchAgent()

    def run_agent(self, **kwargs):
        return self.agent.run(Requirements(**kwargs), self.catalog)

    def test_category_required(self):
        with self.assertRaises(ValueError):
            self.agent.run(Requirements(), self.catalog)

    def test_only_requested_category(self):
        res = self.run_agent(category="headphones")
        self.assertTrue(all(c.product.category == "headphones" for c in res.candidates))

    def test_budget_is_respected(self):
        res = self.run_agent(category="laptop", max_budget=900)
        self.assertTrue(res.candidates)
        self.assertTrue(all(c.product.price <= 900 for c in res.candidates))
        self.assertFalse(res.relaxed_budget)

    def test_min_budget(self):
        res = self.run_agent(category="laptop", min_budget=1000)
        self.assertTrue(all(c.product.price >= 1000 for c in res.candidates))

    def test_budget_is_stretched_once(self):
        res = self.run_agent(category="laptop", max_budget=500)   # cheapest is 549
        self.assertTrue(res.relaxed_budget)
        self.assertEqual([c.product.id for c in res.candidates], ["lap-003"])
        self.assertTrue(any("stretched" in n for n in res.notes))

    def test_hopeless_budget_gives_nothing(self):
        res = self.run_agent(category="laptop", max_budget=100)
        self.assertEqual(res.candidates, [])

    def test_shortlist_size_limit(self):
        self.assertLessEqual(len(self.run_agent(category="laptop").candidates), 4)
        small = ProductResearchAgent(max_results=2).run(Requirements(category="laptop"), self.catalog)
        self.assertEqual(len(small.candidates), 2)

    def test_relevance_orders_results(self):
        res = self.run_agent(category="laptop", tags=["coding", "travel"])
        relevances = [c.relevance for c in res.candidates]
        self.assertEqual(relevances, sorted(relevances, reverse=True))
        self.assertEqual(res.candidates[0].relevance, 1.0)
        self.assertEqual(set(res.candidates[0].matched_tags), {"coding", "travel"})

    def test_zero_relevance_dropped_when_others_match(self):
        res = self.run_agent(category="laptop", tags=["gaming"])
        self.assertEqual([c.product.id for c in res.candidates], ["lap-004"])

    def test_zero_relevance_kept_if_nothing_matches(self):
        res = self.run_agent(category="backpack", tags=["gaming"])
        self.assertTrue(res.candidates)
        self.assertTrue(all(c.relevance == 0 for c in res.candidates))

    def test_brand_filter(self):
        res = self.run_agent(category="laptop", brands=["Vertex"])
        self.assertTrue(all(c.product.brand == "Vertex" for c in res.candidates))

    def test_brand_filter_ignored_if_it_empties_everything(self):
        res = self.run_agent(category="laptop", brands=["Stride"])
        self.assertTrue(res.candidates)
        self.assertTrue(any("ignored" in n for n in res.notes))

    def test_min_specs_are_hard(self):
        res = self.run_agent(category="laptop", min_specs={"ram_gb": 32})
        self.assertTrue(res.candidates)
        self.assertTrue(all(c.product.specs["ram_gb"] >= 32 for c in res.candidates))

    def test_irrelevant_spec_is_ignored_not_fatal(self):
        res = self.run_agent(category="backpack", min_specs={"ram_gb": 16})
        self.assertTrue(res.candidates)
        self.assertTrue(any("Ignored" in n for n in res.notes))

    def test_no_tags_gives_neutral_relevance(self):
        res = self.run_agent(category="laptop")
        self.assertTrue(all(c.relevance == 0.5 for c in res.candidates))

    def test_works_with_a_custom_catalog(self):
        cat = make_catalog(make_laptop("a", "A"), make_laptop("b", "B"))
        res = self.agent.run(Requirements(category="laptop"), cat)
        self.assertEqual(res.considered, 2)

    def test_empty_category(self):
        res = self.agent.run(Requirements(category="laptop"), make_catalog())
        self.assertEqual(res.candidates, [])


if __name__ == "__main__":
    unittest.main()
