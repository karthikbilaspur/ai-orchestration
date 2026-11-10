"""Dataclasses for Project 20."""
from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class Requirement:
    raw_text: str = ""
    budget: float = 0.0
    quantity: int = 1
    specs: Dict[str, str] = field(default_factory=dict)
    max_delivery_days: int = 30
    min_warranty_years: int = 1
    must_haves: List[str] = field(default_factory=list)

@dataclass
class Vendor:
    id: str; name: str; unit_price: float; currency: str = "INR"
    specs: Dict[str, str] = field(default_factory=dict)
    delivery_days: int = 30; warranty_years: int = 1
    reliability_score: float = 70.0; rating: float = 4.0
    support: str = "Standard"; past_issues: int = 0

@dataclass
class VendorScore:
    vendor: Vendor; price_score: float; spec_score: float
    risk_score: float; delivery_score: float; total_score: float
    total_cost: float; risks: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
