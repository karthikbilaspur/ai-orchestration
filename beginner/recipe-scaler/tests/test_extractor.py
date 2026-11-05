import unittest
from src.extractor import extract_with_llm_mock

class TestExtractor(unittest.TestCase):
    def test_extract(self):
        inp = "This pasta recipe is for 2 people: 200g pasta, 100ml cream. Make it for 5 people"
        data = extract_with_llm_mock(inp)
        self.assertEqual(data["original_servings"], 2)
        self.assertEqual(data["new_servings"], 5)
        self.assertEqual(len(data["ingredients"]), 2)
        self.assertEqual(data["scale_factor"], 2.5)

if __name__ == "__main__":
    unittest.main()