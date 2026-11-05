import unittest
from src.scaler import scale_ingredients, generate_shopping_list

class TestScaler(unittest.TestCase):
    def test_scaling(self):
        ingredients = [{"name": "pasta", "quantity": 200, "unit": "g"}]
        scaled, factor = scale_ingredients(ingredients, 2, 5)
        self.assertEqual(factor, 2.5)
        self.assertEqual(scaled[0]["quantity"], 500)

    def test_shopping_list(self):
        scaled = [{"name": "pasta", "quantity": 500, "unit": "g", "original_quantity": 200}]
        lst = generate_shopping_list(scaled)
        self.assertIn("500g pasta", lst[0])

    def test_zero_servings(self):
        with self.assertRaises(ValueError):
            scale_ingredients([], 0, 5)

if __name__ == "__main__":
    unittest.main()