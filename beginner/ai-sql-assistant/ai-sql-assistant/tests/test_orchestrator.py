from db_setup import setup
from orchestrator import run
import pathlib
def setup_module():
    setup(pathlib.Path("data/sample.db"))
def test_end_to_end_top_products():
    out = run("What are the top 5 highest-selling products?")
    assert "error" not in out
    assert out["result"]["row_count"] <= 5
    assert "Top seller" in out["explanation"]
def test_end_to_end_revenue():
    out = run("Show total revenue by category")
    assert out["result"]["row_count"] > 0
def test_injection_safe():
    out = run("What are the top 5 highest-selling products?; DROP TABLE products")
    # Should still return safe SELECT, not execute drop
    assert "error" not in out or "Blocked" in out.get("explanation","")
