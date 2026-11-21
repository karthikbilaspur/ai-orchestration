import unittest

from shopping_assistant.catalog import (CATEGORY_SPECS, Catalog, get_spec_meta,
                                        load_default_catalog, resolve_priority)


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.catalog = load_default_catalog()

    def test_ids_are_unique(self):
        ids = [p.id for p in self.catalog.all()]
        self.assertEqual(len(ids), len(set(ids)))

    def test_duplicate_ids_are_rejected(self):
        p = self.catalog.all()[0]
        with self.assertRaises(ValueError):
            Catalog([p, p])

    def test_every_category_has_enough_products(self):
        for category in CATEGORY_SPECS:
            self.assertGreaterEqual(len(self.catalog.by_category(category)), 4, category)

    def test_every_product_has_all_specs_of_its_category(self):
        for p in self.catalog.all():
            for meta in CATEGORY_SPECS[p.category]:
                self.assertIn(meta.key, p.specs, f"{p.id} lacks {meta.key}")

    def test_values_are_sane(self):
        for p in self.catalog.all():
            self.assertGreater(p.price, 0)
            self.assertTrue(0 <= p.rating <= 5)
            self.assertTrue(p.tags)

    def test_get_and_brands(self):
        self.assertEqual(self.catalog.get("lap-001").name, "Nimbus AirBook 14")
        self.assertIsNone(self.catalog.get("nope"))
        self.assertIn("Nimbus", self.catalog.brands())

    def test_priority_resolution(self):
        self.assertEqual(resolve_priority("laptop", "battery"), "battery_hours")
        self.assertEqual(resolve_priority("smartphone", "battery"), "battery_mah")
        self.assertIsNone(resolve_priority("backpack", "camera"))

    def test_spec_meta_lookup(self):
        self.assertFalse(get_spec_meta("laptop", "weight_kg").higher_is_better)
        self.assertEqual(get_spec_meta("laptop", "price").key, "price")
        self.assertIsNone(get_spec_meta("laptop", "nonsense"))


if __name__ == "__main__":
    unittest.main()
