import unittest, sys, pathlib, json
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from models import Vendor
from orchestrator import Orchestrator
class TestOrchestrator(unittest.TestCase):
    def test_end_to_end(self):
        vendors=[Vendor(**v) for v in json.loads(pathlib.Path("data/vendors.json").read_text())]
        req, scores, winner, rationale = Orchestrator().run("Need 50 laptops, budget 4000000 INR, 16GB RAM, 512GB SSD, delivery within 14 days, 3 year warranty", vendors)
        self.assertEqual(len(scores), 3); self.assertIn(winner.vendor.name, [v.name for v in vendors])
    def test_bad_weights_raise(self):
        with self.assertRaises(AssertionError): Orchestrator({"price":1.0,"spec_fit":1.0,"risk":0,"delivery":0})
if __name__=="__main__": unittest.main()
