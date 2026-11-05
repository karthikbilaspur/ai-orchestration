
import unittest
from calculator import calculate_bill

class TestExpenseSplitter(unittest.TestCase):
    
    def test_inclusive_gst_case(self):
        result = calculate_bill(3480, 18, 10, 4, gst_inclusive=True)
        self.assertAlmostEqual(result['base_amount'], 2949.15, delta=1)
        self.assertEqual(result['final_total'], 3828.0)
        self.assertEqual(result['per_person'], 957.0)

    def test_exclusive_gst_case(self):
        result = calculate_bill(1000, 18, 0, 2, gst_inclusive=False)
        self.assertEqual(result['subtotal'], 1180)
        self.assertEqual(result['per_person'], 590)

    def test_only_tip(self):
        result = calculate_bill(2000, 0, 10, 4, gst_inclusive=True)
        self.assertEqual(result['final_total'], 2200)
        self.assertEqual(result['per_person'], 550)

    def test_no_tax_no_tip(self):
        result = calculate_bill(1000, 0, 0, 1, True)
        self.assertEqual(result['final_total'], 1000)

if __name__ == '__main__':
    unittest.main()
