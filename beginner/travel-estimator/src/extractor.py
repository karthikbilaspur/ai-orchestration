"""
LLM Extractor Module - Simulates LLM entity extraction
In production, replace regex with OpenAI / Gemini / Llama API call.
"""
import re

def extract_travel_info(text: str) -> dict:
    """
    Extracts distance, rate, speed, source, destination from natural language.
    """
    text_lower = text.lower()
    
    # Defaults
    result = {
        "source": None,
        "destination": None,
        "distance_km": None,
        "rate_per_km": None,
        "avg_speed_kmph": 30.0
    }

    # Extract distance: "32km", "32 km", "distance is 32km"
    dist_match = re.search(r'(\d+(?:\.\d+)?)\s*km', text_lower)
    if dist_match:
        result["distance_km"] = float(dist_match.group(1))

    # Extract rate: "18rs per km", "18 rs/km", "₹18 per km"
    rate_match = re.search(r'(?:rs\.?|₹|\$)?\s*(\d+(?:\.\d+)?)\s*(?:rs)?\s*(?:per|\/)\s*km', text_lower)
    if rate_match:
        result["rate_per_km"] = float(rate_match.group(1))
    else:
        # fallback: "charges 18rs"
        rate_match2 = re.search(r'charg\w*\s+(\d+)\s*rs', text_lower)
        if rate_match2:
            result["rate_per_km"] = float(rate_match2.group(1))

    # Extract speed: "avg speed is 30 km/h", "speed 30"
    speed_match = re.search(r'(?:speed|avg)\D*(\d+(?:\.\d+)?)\s*(?:km/h|kmph|kph)', text_lower)
    if speed_match:
        result["avg_speed_kmph"] = float(speed_match.group(1))

    # Extract source -> destination: "from X to Y"
    route_match = re.search(r'from\s+([a-zA-Z\s]+?)\s+to\s+([a-zA-Z\s]+?)(?:,|\.|$)', text_lower)
    if route_match:
        result["source"] = route_match.group(1).strip().title()
        result["destination"] = route_match.group(2).strip().title()

    return result
