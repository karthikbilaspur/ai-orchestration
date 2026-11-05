import unittest
from src.extractor_gemini import regex_extract, extract_travel_info
from src.calculator import calculate_cost, calculate_time
from src.estimator import run_estimation

class TestV2(unittest.TestCase):
    def test_regex_basic(self):
        data = regex_extract("Indiranagar to Airport 32km at 18rs per km speed 30 km/h")
        self.assertEqual(data["distance_km"], 32)
        self.assertEqual(data["rate_per_km"], 18)
        self.assertEqual(data["source"], "Indiranagar")

    def test_mode_detection(self):
        self.assertEqual(regex_extract("go by cab 20km at 25rs/km")["mode"], "cab")
        self.assertEqual(regex_extract("go by bike 10km at 10rs/km")["mode"], "bike")

    def test_traffic_detection(self):
        self.assertEqual(regex_extract("peak traffic 32km at 18rs/km")["traffic"], "heavy")

    def test_cost_with_mode(self):
        c = calculate_cost(32, 18, mode="cab", round_trip=False)
        # cab 1.5x: 32*18*1.5 = 864
        self.assertEqual(c["total_cost"], 864)

    def test_round_trip(self):
        c = calculate_cost(32, 18, round_trip=True)
        self.assertEqual(c["distance_charged"], 64)
        self.assertEqual(c["total_cost"], 1152)

    def test_time_with_traffic(self):
        t = calculate_time(32, 30, traffic="heavy")
        self.assertLess(t["effective_speed"], 30)  # heavy reduces speed

    def test_full_flow_no_gemini(self):
        result = run_estimation("Koramangala to Whitefield 20km at 20rs per km speed 40 km/h", save_output=False, use_gemini=False)
        self.assertEqual(result["cost_info"]["total_cost"], 400)
        self.assertIn("Koramangala", result["explanation"])

    def test_invalid(self):
        with self.assertRaises(ValueError):
            run_estimation("hello world", save_output=False, use_gemini=False)

if __name__ == "__main__":
    unittest.main()
