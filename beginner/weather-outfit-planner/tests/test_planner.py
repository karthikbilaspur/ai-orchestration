import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from llm_parser import extract_with_rules
from outfit_logic import recommend_outfit

def test_city_extract():
    parsed = extract_with_rules("Should I carry an umbrella in Bangalore tomorrow?")
    assert parsed["city"] == "Bangalore"
    assert parsed["intent"]["umbrella"] == True

def test_outfit_hot():
    forecast = {"temp_c": 32, "rain_prob": 10, "description": "clear sky", "wind_kmh": 5}
    intent = {"activity": "general"}
    res = recommend_outfit(forecast, intent)
    assert "t-shirt" in res["outfit"]
    assert res["umbrella_needed"] == "No"

def test_outfit_rainy_run():
    forecast = {"temp_c": 24, "rain_prob": 80, "description": "light rain", "wind_kmh": 10}
    intent = {"activity": "morning run"}
    res = recommend_outfit(forecast, intent)
    assert res["umbrella_needed"] == "Yes"
    assert "running" in res["outfit"].lower()

def test_output_folder_creation():
    # Ensure main creates output
    import main
    data = main.run_planner("Should I carry an umbrella in Bangalore tomorrow? And what should I wear for a morning run?")
    assert os.path.exists("output")
    assert "recommendation" in data
