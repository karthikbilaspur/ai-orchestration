"""
AI Weather Outfit Planner - Orchestration Flow
1. LLM extracts -> city, date
2. Call Weather API tool -> get forecast
3. Send forecast back to LLM/logic -> recommendation
4. Save auto output to output/
"""
import os, json
from datetime import datetime
from llm_parser import extract_with_llm
from weather_service import WeatherService
from outfit_logic import recommend_outfit
from air_quality import get_air_quality

def run_planner(user_query: str):
    print(f"\n> User: {user_query}")

    # Step 1: LLM Extract
    parsed = extract_with_llm(user_query)
    print(f"[LLM] Parsed -> {parsed}")

    # Step 2: Weather API
    ws = WeatherService()
    forecast = ws.get_forecast(parsed["city"], parsed["date"])
    print(f"[Weather API] Forecast -> {forecast}")

    # Step 3: Optional AQI (Stretch)
    aqi = get_air_quality()
    print(f"[AQI API] -> {aqi}")

    # Step 4: LLM/Logic Recommendation
    result = recommend_outfit(forecast, parsed["intent"], aqi)
    print(f"[Recommendation] {result['final_text']}")

    # Step 5: Auto-save output to output/ folder
    os.makedirs("output", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_data = {
        "query": user_query,
        "parsed": parsed,
        "forecast": forecast,
        "air_quality": aqi,
        "recommendation": result,
        "generated_at": timestamp
    }

    json_path = f"output/result_{timestamp}.json"
    txt_path = f"output/result_{timestamp}.txt"

    with open(json_path, "w") as f:
        json.dump(output_data, f, indent=2)

    with open(txt_path, "w") as f:
        f.write(f"AI Weather Outfit Planner\n")
        f.write(f"Query: {user_query}\n")
        f.write(f"City: {parsed['city']} | Date: {parsed['date']}\n")
        f.write(f"Forecast: {forecast}\n")
        f.write(f"AQI: {aqi}\n\n")
        f.write(f"Recommendation: {result['final_text']}\n")

    print(f"\n✓ Saved to {json_path} and {txt_path}")
    return output_data

if __name__ == "__main__":
    # Example from your prompt
    query = input("Ask (e.g., Should I carry an umbrella in Bangalore tomorrow? And what should I wear for a morning run?):\n> ")
    if not query.strip():
        query = "Should I carry an umbrella in Bangalore tomorrow? And what should I wear for a morning run?"
    run_planner(query)
