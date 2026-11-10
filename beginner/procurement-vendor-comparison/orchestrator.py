"""Orchestration: Requirement -> Parallel(Vendor, Price, Risk) -> Decision."""
from concurrent.futures import ThreadPoolExecutor
from agents import RequirementAgent, VendorAnalysisAgent, PricingAgent, RiskAgent, DecisionAgent
from models import VendorScore
from utils import log

class Orchestrator:
    def __init__(self, weights=None):
        self.weights = weights or {"price":0.35,"spec_fit":0.30,"risk":0.20,"delivery":0.15}
        assert abs(sum(self.weights.values())-1.0) < 1e-6, "Weights must sum to 1.0"
    def run(self, req_text, vendors):
        log("RequirementAgent: parsing requirements")
        req = RequirementAgent().run(req_text)
        log(f"Parsed: budget={req.budget}, qty={req.quantity}, specs={req.specs}")
        all_costs = [v.unit_price*req.quantity for v in vendors]
        def analyse(v):
            spec, strengths = VendorAnalysisAgent().run(req, v)
            price, total = PricingAgent().run(req, v, all_costs)
            risk, delivery, risks = RiskAgent().run(req, v)
            return VendorScore(v, price, spec, risk, delivery, 0, total, risks, strengths)
        log("Parallel: VendorAnalysis + Pricing + Risk (ThreadPoolExecutor)")
        with ThreadPoolExecutor(max_workers=3) as ex:
            scores = list(ex.map(analyse, vendors))
        winner, rationale = DecisionAgent().run(scores, self.weights)
        log(f"DecisionAgent: winner={winner.vendor.name} score={winner.total_score}")
        return req, scores, winner, rationale
