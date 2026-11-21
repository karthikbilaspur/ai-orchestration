"""Small helpers shared by the test files."""
from shopping_assistant.catalog import Catalog
from shopping_assistant.models import Product


def make_laptop(pid="t-1", name="Test Laptop", price=800.0, rating=4.0, tags=("coding",), **spec_overrides):
    specs = {"ram_gb": 16, "storage_gb": 512, "battery_hours": 10, "weight_kg": 1.5}
    specs.update(spec_overrides)
    return Product(pid, name, "laptop", "Testco", price, rating, specs, tuple(tags))


def make_catalog(*products):
    return Catalog(products)


def scripted(answers):
    """An input() stand-in that replays `answers` and records the prompts."""
    queue = list(answers)
    prompts = []

    def fake(prompt):
        prompts.append(prompt)
        return queue.pop(0) if queue else ""

    fake.prompts = prompts
    return fake
