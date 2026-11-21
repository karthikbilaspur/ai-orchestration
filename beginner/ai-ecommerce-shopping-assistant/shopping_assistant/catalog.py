"""The local sample catalog (all brands, products and prices are made up).

Nothing here touches the internet, so the demo needs no API keys.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional

from .config import CURRENCY
from .models import Product


@dataclass(frozen=True)
class SpecMeta:
    """Describes one comparable spec of a category."""

    key: str
    label: str
    unit: str = ""
    higher_is_better: bool = True
    kind: str = "num"          # "num" or "bool"


CATEGORY_SPECS: Dict[str, List[SpecMeta]] = {
    "laptop": [
        SpecMeta("ram_gb", "RAM", "GB"),
        SpecMeta("storage_gb", "Storage", "GB"),
        SpecMeta("battery_hours", "Battery life", "h"),
        SpecMeta("weight_kg", "Weight", "kg", higher_is_better=False),
    ],
    "headphones": [
        SpecMeta("battery_hours", "Battery life", "h"),
        SpecMeta("weight_g", "Weight", "g", higher_is_better=False),
        SpecMeta("noise_cancelling", "Noise cancelling", kind="bool"),
    ],
    "smartphone": [
        SpecMeta("ram_gb", "RAM", "GB"),
        SpecMeta("storage_gb", "Storage", "GB"),
        SpecMeta("battery_mah", "Battery", "mAh"),
        SpecMeta("camera_mp", "Main camera", "MP"),
        SpecMeta("weight_g", "Weight", "g", higher_is_better=False),
    ],
    "running_shoes": [
        SpecMeta("weight_g", "Weight", "g", higher_is_better=False),
        SpecMeta("cushion", "Cushioning", "/5"),
        SpecMeta("durability_km", "Durability", "km"),
    ],
    "backpack": [
        SpecMeta("capacity_l", "Capacity", "L"),
        SpecMeta("weight_kg", "Weight", "kg", higher_is_better=False),
        SpecMeta("laptop_size_in", "Fits laptop up to", "in"),
        SpecMeta("water_resistant", "Water resistant", kind="bool"),
    ],
}

CATEGORY_LABELS: Dict[str, str] = {
    "laptop": "laptop",
    "headphones": "headphones",
    "smartphone": "smartphone",
    "running_shoes": "running shoes",
    "backpack": "backpack",
}

# Words a shopper might say  ->  the spec that word is about, per category.
PRIORITY_SPECS: Dict[str, Dict[str, str]] = {
    "battery": {"laptop": "battery_hours", "headphones": "battery_hours", "smartphone": "battery_mah"},
    "light": {"laptop": "weight_kg", "headphones": "weight_g", "smartphone": "weight_g",
              "running_shoes": "weight_g", "backpack": "weight_kg"},
    "camera": {"smartphone": "camera_mp"},
    "storage": {"laptop": "storage_gb", "smartphone": "storage_gb"},
    "performance": {"laptop": "ram_gb", "smartphone": "ram_gb"},
    "cushion": {"running_shoes": "cushion"},
    "capacity": {"backpack": "capacity_l"},
    "durability": {"running_shoes": "durability_km"},
    "value": {c: "price" for c in CATEGORY_SPECS},
}

PRICE_META = SpecMeta("price", "Price", CURRENCY, higher_is_better=False)
RATING_META = SpecMeta("rating", "Customer rating", "/5")


def resolve_priority(category: str, word: str) -> Optional[str]:
    """Translate a priority word ('battery') into a spec key for a category."""
    return PRIORITY_SPECS.get(word, {}).get(category)


def get_spec_meta(category: str, key: str) -> Optional[SpecMeta]:
    if key == "price":
        return PRICE_META
    if key == "rating":
        return RATING_META
    for meta in CATEGORY_SPECS.get(category, []):
        if meta.key == key:
            return meta
    return None


def _p(pid, name, category, brand, price, rating, specs, tags) -> Product:
    return Product(pid, name, category, brand, price, rating, specs, tuple(tags))


SAMPLE_PRODUCTS: List[Product] = [
    # ------------------------------------------------------------ laptops --
    _p("lap-001", "Nimbus AirBook 14", "laptop", "Nimbus", 899, 4.5,
       {"ram_gb": 16, "storage_gb": 512, "battery_hours": 14, "weight_kg": 1.2},
       ["travel", "office", "student", "coding"]),
    _p("lap-002", "Vertex ProBook 15", "laptop", "Vertex", 1099, 4.4,
       {"ram_gb": 32, "storage_gb": 1024, "battery_hours": 11, "weight_kg": 1.8},
       ["coding", "office", "creative"]),
    _p("lap-003", "Aurora Go 15", "laptop", "Aurora", 549, 4.0,
       {"ram_gb": 8, "storage_gb": 256, "battery_hours": 8, "weight_kg": 1.7},
       ["student", "office"]),
    _p("lap-004", "Vertex Titan G16", "laptop", "Vertex", 1599, 4.6,
       {"ram_gb": 32, "storage_gb": 1024, "battery_hours": 6, "weight_kg": 2.5},
       ["gaming", "creative", "coding"]),
    _p("lap-005", "Orbit Slim 13", "laptop", "Orbit", 1099, 4.8,
       {"ram_gb": 16, "storage_gb": 512, "battery_hours": 18, "weight_kg": 1.24},
       ["travel", "student", "coding", "creative", "office"]),
    _p("lap-006", "Aurora Everyday 14", "laptop", "Aurora", 749, 4.2,
       {"ram_gb": 16, "storage_gb": 512, "battery_hours": 10, "weight_kg": 1.6},
       ["student", "office", "coding"]),
    # --------------------------------------------------------- headphones --
    _p("hp-001", "Pulse Studio ANC", "headphones", "Pulse", 249, 4.6,
       {"battery_hours": 40, "weight_g": 250, "noise_cancelling": 1},
       ["music", "travel", "wireless", "noise-cancelling", "office", "coding"]),
    _p("hp-002", "Pulse Beat Lite", "headphones", "Pulse", 59, 3.9,
       {"battery_hours": 20, "weight_g": 180, "noise_cancelling": 0},
       ["wireless", "music", "gym"]),
    _p("hp-003", "Aurora Buds Pro", "headphones", "Aurora", 149, 4.4,
       {"battery_hours": 30, "weight_g": 5, "noise_cancelling": 1},
       ["wireless", "travel", "gym", "noise-cancelling", "office"]),
    _p("hp-004", "Summit Gamer H7", "headphones", "Summit", 99, 4.2,
       {"battery_hours": 25, "weight_g": 320, "noise_cancelling": 0},
       ["gaming", "wireless"]),
    _p("hp-005", "Nimbus Focus 700", "headphones", "Nimbus", 349, 4.7,
       {"battery_hours": 35, "weight_g": 254, "noise_cancelling": 1},
       ["noise-cancelling", "music", "office", "travel", "wireless", "coding"]),
    # -------------------------------------------------------- smartphones --
    _p("ph-001", "Orbit X1", "smartphone", "Orbit", 599, 4.4,
       {"ram_gb": 8, "storage_gb": 128, "battery_mah": 4500, "camera_mp": 50, "weight_g": 190},
       ["photography", "travel", "office"]),
    _p("ph-002", "Orbit X1 Pro", "smartphone", "Orbit", 899, 4.6,
       {"ram_gb": 12, "storage_gb": 256, "battery_mah": 5000, "camera_mp": 108, "weight_g": 205},
       ["photography", "gaming", "creative", "travel"]),
    _p("ph-003", "Nimbus Spark", "smartphone", "Nimbus", 249, 4.0,
       {"ram_gb": 6, "storage_gb": 128, "battery_mah": 5000, "camera_mp": 48, "weight_g": 195},
       ["student"]),
    _p("ph-004", "Vertex Titan Phone", "smartphone", "Vertex", 1099, 4.7,
       {"ram_gb": 16, "storage_gb": 512, "battery_mah": 5200, "camera_mp": 200, "weight_g": 225},
       ["gaming", "photography", "creative"]),
    _p("ph-005", "Aurora Lite", "smartphone", "Aurora", 399, 4.2,
       {"ram_gb": 8, "storage_gb": 256, "battery_mah": 5500, "camera_mp": 64, "weight_g": 185},
       ["student", "travel", "office"]),
    # ------------------------------------------------------ running shoes --
    _p("sh-001", "Stride Swift 5", "running_shoes", "Stride", 129, 4.5,
       {"weight_g": 240, "cushion": 3, "durability_km": 800},
       ["running", "daily", "marathon"]),
    _p("sh-002", "Stride CloudRun", "running_shoes", "Stride", 149, 4.6,
       {"weight_g": 280, "cushion": 5, "durability_km": 900},
       ["running", "daily", "gym"]),
    _p("sh-003", "Terra TrailBlazer", "running_shoes", "Terra", 139, 4.4,
       {"weight_g": 300, "cushion": 4, "durability_km": 1000},
       ["trail", "hiking", "running"]),
    _p("sh-004", "Summit Racer Pro", "running_shoes", "Summit", 219, 4.7,
       {"weight_g": 200, "cushion": 3, "durability_km": 500},
       ["marathon", "running"]),
    _p("sh-005", "Pulse Everyday", "running_shoes", "Pulse", 79, 4.0,
       {"weight_g": 290, "cushion": 3, "durability_km": 600},
       ["daily", "gym", "running"]),
    # ---------------------------------------------------------- backpacks --
    _p("bp-001", "Terra Trek 40", "backpack", "Terra", 129, 4.5,
       {"capacity_l": 40, "weight_kg": 1.4, "laptop_size_in": 15, "water_resistant": 1},
       ["travel", "hiking"]),
    _p("bp-002", "Nimbus Commute 25", "backpack", "Nimbus", 79, 4.4,
       {"capacity_l": 25, "weight_kg": 0.9, "laptop_size_in": 16, "water_resistant": 1},
       ["office", "student", "travel"]),
    _p("bp-003", "Orbit Campus 30", "backpack", "Orbit", 49, 4.1,
       {"capacity_l": 30, "weight_kg": 0.8, "laptop_size_in": 15, "water_resistant": 0},
       ["student"]),
    _p("bp-004", "Summit Daypack 20", "backpack", "Summit", 59, 4.2,
       {"capacity_l": 20, "weight_kg": 0.6, "laptop_size_in": 13, "water_resistant": 1},
       ["hiking", "travel"]),
    _p("bp-005", "Vertex Pro Laptop Pack", "backpack", "Vertex", 109, 4.6,
       {"capacity_l": 28, "weight_kg": 1.1, "laptop_size_in": 17, "water_resistant": 1},
       ["office", "coding", "travel"]),
]


class Catalog:
    """A small read-only product store."""

    def __init__(self, products: Iterable[Product]):
        self._products: List[Product] = list(products)
        ids = [p.id for p in self._products]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate product ids in catalog")

    def __len__(self) -> int:
        return len(self._products)

    def all(self) -> List[Product]:
        return list(self._products)

    def by_category(self, category: str) -> List[Product]:
        return [p for p in self._products if p.category == category]

    def get(self, product_id: str) -> Optional[Product]:
        for p in self._products:
            if p.id == product_id:
                return p
        return None

    def categories(self) -> List[str]:
        seen: List[str] = []
        for p in self._products:
            if p.category not in seen:
                seen.append(p.category)
        return seen

    def brands(self) -> List[str]:
        return sorted({p.brand for p in self._products})


def load_default_catalog() -> Catalog:
    return Catalog(SAMPLE_PRODUCTS)
