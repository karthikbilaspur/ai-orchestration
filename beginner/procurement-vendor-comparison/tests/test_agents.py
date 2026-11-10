import unittest, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from agents import RequirementAgent, PricingAgent, RiskAgent, DecisionAgent
from models import Requirement, Vendor, VendorScore
class TestAgents(unittest.TestCase):
    def test_requirement_parsing(self):
        r = RequirementAgent().run("Need 50 laptops, budget 4000000 INR, 16GB RAM, 512GB SSD, delivery within 14 days, 3 year warranty")
        self.assertEqual(r.quantity, 50); self.assertEqual(r.budget, 4000000); self.assertEqual(r.specs["RAM"], "16GB")
    def test_pricing_cheapest_wins(self):
        v = Vendor("V1","A",64000); req = Requirement(quantity=10)
        s, total = PricingAgent().run(req, v, [640000, 720000]); self.assertEqual(s, 100.0); self.assertEqual(total, 640000)
    def test_risk_late_delivery_flagged(self):
        v = Vendor("V1","A",100, delivery_days=30, warranty_years=1, reliability_score=80)
        req = Requirement(max_delivery_days=14, min_warranty_years=3)
        score, delivery, risks = RiskAgent().run(req, v); self.assertTrue(any("delivery" in x.lower() for x in risks))
    def test_decision_weighted(self):
        a = VendorScore(Vendor("1","A",100), 80, 90, 80, 80, 0, 1000)
        b = VendorScore(Vendor("2","B",100), 60, 60, 60, 60, 0, 1000)
        w,_ = DecisionAgent().run([a,b], {"price":.35,"spec_fit":.30,"risk":.20,"delivery":.15})
        self.assertEqual(w.vendor.name, "A")
if __name__=="__main__": unittest.main()
