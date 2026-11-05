"""
Core Logic: weather -> outfit + umbrella decision
"""
def recommend_outfit(forecast: dict, intent: dict, air_quality=None):
    temp = forecast["temp_c"]
    rain_prob = forecast["rain_prob"]
    wind = forecast["wind_kmh"]
    desc = forecast["description"]

    # Outfit Logic
    if temp >= 30:
        base = "light t-shirt, shorts, breathable shoes"
    elif temp >= 24:
        base = "light t-shirt + light trousers, sneakers"
    elif temp >= 18:
        base = "full-sleeve shirt + jeans + light jacket"
    else:
        base = "sweater/jacket + jeans + closed shoes"

    # Activity specific
    activity = intent.get("activity", "general")
    if "run" in activity:
        if temp >= 24:
            base = "moisture-wicking t-shirt, running shorts, running shoes"
        else:
            base = "light track pants + breathable long-sleeve + running shoes"

    # Umbrella logic
    umbrella = "Yes" if rain_prob >= 30 or "rain" in desc else "No"
    umbrella_reason = f"{rain_prob}% rain chance, {desc}"

    # Build final message
    recommendation = f"{rain_prob}% rain, {temp}°C ({desc}). Wear: {base}."
    if umbrella == "Yes":
        recommendation += " Carry umbrella / light rain jacket."
    else:
        recommendation += " No umbrella needed."

    if wind > 25:
        recommendation += f" Windy ({wind} km/h) - avoid loose cap."

    if air_quality:
        if air_quality.get("aqi", 1) >= 4:
            recommendation += f" AQI is {air_quality['label']} - consider mask for run."

    return {
        "outfit": base,
        "umbrella_needed": umbrella,
        "umbrella_reason": umbrella_reason,
        "final_text": recommendation
    }
