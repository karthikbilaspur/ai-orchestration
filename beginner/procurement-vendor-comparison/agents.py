"""All 5 agents for Project 20."""
import re
from models import Requirement, Vendor, VendorScore

class RequirementAgent:
    """Extracts budget, specs, requirements from free text."""
    def run(self, text: str) -> Requirement:
        r = Requirement(raw_text=text)
        m = re.search(r"budget[^0-9]*([0-9,]+)", text, re.I)
        if m: r.budget = float(m.group(1).replace(",", ""))
        m = re.search(r"(\d+)\s*(laptops|units|pcs|seats|licenses)", text, re.I)
        if m: r.quantity = int(m.group(1))
        m = re.search(r"(\d+)\s*GB\s*RAM", text, re.I)
        if m: r.specs["RAM"] = f"{m.group(1)}GB"
        m = re.search(r"(\d+)\s*GB\s*SSD", text, re.I)
        if m: r.specs["SSD"] = f"{m.group(1)}GB"
        m = re.search(r"within\s*(\d+)\s*days", text, re.I)
        if m: r.max_delivery_days = int(m.group(1))
        m = re.search(r"(\d+)\s*year warranty", text, re.I)
        if m: r.min_warranty_years = int(m.group(1))
        return r

class VendorAnalysisAgent:
    """Evaluates spec fit."""
    def run(self, req: Requirement, vendor: Vendor) -> tuple[float, list]:
        if not req.specs: return 80.0, ["No strict specs — generic fit"]
        matched, strengths = 0, []
        for k, v in req.specs.items():
            if vendor.specs.get(k, "").lower() == v.lower():
                matched += 1; strengths.append(f"Matches {k}={v}")
            else:
                strengths.append(f"Mismatch {k}: need {v}, offers {vendor.specs.get(k,'—')}")
        return round(matched / len(req.specs) * 100, 1), strengths

class PricingAgent:
    """Compares costs. Higher score = cheaper relative to budget / peers."""
    def run(self, req: Requirement, vendor: Vendor, all_costs: list) -> tuple[float, float]:
        total = vendor.unit_price * req.quantity
        cheapest = min(all_costs) if all_costs else total
        # 100 if cheapest, penalise proportionally, plus budget check
        score = max(0, 100 - (total - cheapest) / cheapest * 100) if cheapest else 0
        if req.budget and total > req.budget: score = min(score, 40.0)
        return round(score, 1), round(total, 2)

class RiskAgent:
    """Checks delivery, warranty, reliability."""
    def run(self, req: Requirement, vendor: Vendor) -> tuple[float, float, list]:
        risks, score = [], 100.0
        if vendor.delivery_days > req.max_delivery_days:
            risks.append(f"Late delivery: {vendor.delivery_days}d > {req.max_delivery_days}d"); score -= 25
        if vendor.warranty_years < req.min_warranty_years:
            risks.append(f"Short warranty: {vendor.warranty_years}y < {req.min_warranty_years}y"); score -= 20
        score = score * 0.5 + vendor.reliability_score * 0.5 - vendor.past_issues * 3
        delivery = max(0, 100 - max(0, vendor.delivery_days - 7) * 4)
        return round(max(0, min(100, score)), 1), round(delivery, 1), risks

class DecisionAgent:
    """Weighted scoring + recommendation."""
    def run(self, scores: list[VendorScore], weights: dict) -> tuple[VendorScore, str]:
        for s in scores:
            s.total_score = round(
                s.price_score*weights["price"] + s.spec_score*weights["spec_fit"]
                + s.risk_score*weights["risk"] + s.delivery_score*weights["delivery"], 1)
        ranked = sorted(scores, key=lambda x: (-x.total_score, x.total_cost, -x.risk_score))
        winner = ranked[0]
        rationale = (f"{winner.vendor.name} wins with {winner.total_score}/100. "
                     f"Total cost ₹{winner.total_cost:,.0f}, spec fit {winner.spec_score}, "
                     f"risk {winner.risk_score}. Runner-up: {ranked[1].vendor.name} ({ranked[1].total_score}).")
        return winner, rationale
