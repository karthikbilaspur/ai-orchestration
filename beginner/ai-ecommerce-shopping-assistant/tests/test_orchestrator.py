import logging
import os
import tempfile
import unittest

from shopping_assistant import ShoppingAssistant
from shopping_assistant.config import DISCLAIMER
from shopping_assistant.logging_config import ROOT_LOGGER_NAME, setup_logging
from tests.helpers import scripted


class EndToEndTests(unittest.TestCase):
    def setUp(self):
        self.assistant = ShoppingAssistant()

    def test_full_pipeline(self):
        result = self.assistant.run("I need a laptop under 1000 for coding and travel, lightweight with good battery")
        self.assertTrue(result.ok)
        self.assertEqual(result.requirements.category, "laptop")
        self.assertTrue(result.research.candidates)
        self.assertTrue(result.comparison.products)
        best = result.recommendation.best.product
        self.assertEqual(best.category, "laptop")
        self.assertLessEqual(best.price, 1000)

    def test_agents_run_in_order(self):
        result = self.assistant.run("headphones under 300")
        names = [s.split(":")[0] for s in result.steps]
        self.assertEqual(names, ["RequirementCollector", "ProductResearch", "Comparison", "Recommendation"])

    def test_unknown_category_stops_with_a_helpful_error(self):
        result = self.assistant.run("something nice")
        self.assertFalse(result.ok)
        self.assertIn("what kind of product", result.error)
        self.assertIsNone(result.research)

    def test_follow_up_questions_rescue_a_vague_request(self):
        result = self.assistant.run("help me", input_fn=scripted(["laptop", "900", "coding"]))
        self.assertTrue(result.ok)
        self.assertEqual(result.requirements.category, "laptop")

    def test_no_match_reports_error(self):
        result = self.assistant.run("a laptop under 50")
        self.assertFalse(result.ok)
        self.assertIn("No products", result.error)
        self.assertIsNone(result.comparison)

    def test_report_contains_all_sections_and_disclaimer(self):
        result = self.assistant.run("running shoes for a marathon, cushioned, max 200")
        report = self.assistant.report(result)
        for heading in ("Requirements", "Research", "Comparison", "Recommendation"):
            self.assertIn(heading, report)
        self.assertIn(DISCLAIMER, report)
        self.assertIn("TOP PICK", report)

    def test_error_report_still_has_disclaimer(self):
        report = self.assistant.report(self.assistant.run("nothing useful"))
        self.assertIn(DISCLAIMER, report)

    def test_assistant_can_never_buy(self):
        forbidden = ("buy", "purchase", "checkout", "cart", "order", "pay")
        names = [n.lower() for n in dir(self.assistant)]
        for word in forbidden:
            self.assertFalse([n for n in names if word in n], f"found a '{word}' method")
        for agent in (self.assistant.collector, self.assistant.researcher,
                      self.assistant.comparer, self.assistant.recommender):
            for word in forbidden:
                self.assertFalse([n for n in dir(agent) if word in n.lower()])

    def test_same_request_gives_same_answer(self):
        a = self.assistant.run("smartphone under 900 for photography, good camera")
        b = self.assistant.run("smartphone under 900 for photography, good camera")
        self.assertEqual(a.recommendation.best.product.id, b.recommendation.best.product.id)

    def test_every_category_works_end_to_end(self):
        for query in ("a laptop", "headphones", "a smartphone", "running shoes", "a backpack"):
            result = self.assistant.run(query)
            self.assertTrue(result.ok, query)

    def test_no_api_keys_or_network_needed(self):
        for var in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY"):
            os.environ.pop(var, None)
        self.assertTrue(ShoppingAssistant().run("laptop under 900").ok)


class LoggingTests(unittest.TestCase):
    def test_steps_are_written_to_the_log_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "log.txt")
            setup_logging(path)
            ShoppingAssistant().run("laptop under 1000 for coding")
            logging.getLogger(ROOT_LOGGER_NAME).handlers[0].flush()
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
            setup_logging(os.devnull)          # release the temp file
        for agent in ("RequirementCollector", "ProductResearch", "Comparison", "Recommendation"):
            self.assertIn(agent, text)
        self.assertIn("New request", text)

    def test_calling_setup_twice_does_not_duplicate_handlers(self):
        setup_logging(os.devnull)
        setup_logging(os.devnull)
        self.assertEqual(len(logging.getLogger(ROOT_LOGGER_NAME).handlers), 1)


if __name__ == "__main__":
    unittest.main()
