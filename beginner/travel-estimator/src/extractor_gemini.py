"""
Gemini-based Extractor - Round 2 Upgrade
Uses Google Gemini with structured JSON output.
Falls back to regex if no API key or API fails.
"""
import json
import re
from .config import GEMINI_API_KEY, GEMINI_MODEL, has_gemini_key

# Fallback regex extractor (always available)
def regex_extract(text: str) -> dict:
    text_lower = text.lower()
    result = {
        "source": None,
        "destination": None,
        "distance_km": None,
        "rate_per_km": None,
        "avg_speed_kmph": 30.0,
        "mode": "auto",
        "traffic": "normal",
        "round_trip": False
    }
    dist = re.search(r'(\d+(?:\.\d+)?)\s*km', text_lower)
    if dist: result["distance_km"] = float(dist.group(1))
    
    rate = re.search(r'(?:rs\.?|₹|\$)?\s*(\d+(?:\.\d+)?)\s*(?:rs)?\s*(?:per|/)\s*km', text_lower)
    if rate: 
        result["rate_per_km"] = float(rate.group(1))
    else:
        rate2 = re.search(r'charg\w*\s+(\d+)\s*rs', text_lower)
        if rate2: result["rate_per_km"] = float(rate2.group(1))
    
    speed = re.search(r'(?:speed|avg)\D*(\d+(?:\.\d+)?)\s*(?:km/h|kmph|kph)', text_lower)
    if speed: result["avg_speed_kmph"] = float(speed.group(1))
    
    route = re.search(r'from\s+([a-zA-Z\s]+?)\s+to\s+([a-zA-Z\s]+?)(?:,|\.|$)', text_lower)
    if not route:
        route = re.search(r'([a-zA-Z]+)\s+to\s+([a-zA-Z]+)', text_lower)
    if route:
        result["source"] = route.group(1).strip().title()
        result["destination"] = route.group(2).strip().title()
    
    # New features: mode detection
    if any(x in text_lower for x in ["cab", "uber", "ola"]): result["mode"] = "cab"
    elif "bike" in text_lower: result["mode"] = "bike"
    elif "metro" in text_lower: result["mode"] = "metro"
    
    if "round" in text_lower or "return" in text_lower: result["round_trip"] = True
    if "peak" in text_lower or "traffic" in text_lower or "rush" in text_lower: result["traffic"] = "heavy"
    
    return result

def gemini_extract(text: str) -> dict:
    """Call Gemini API for structured extraction"""
    if not has_gemini_key():
        print("[INFO] No GEMINI_API_KEY found, using regex fallback")
        return regex_extract(text)
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(GEMINI_MODEL)
        
        prompt = f"""
You are a travel info extractor. Extract from this query:
"{text}"

Return ONLY valid JSON with these keys:
{{
  "source": string or null (e.g. "Indiranagar"),
  "destination": string or null (e.g. "Airport"),
  "distance_km": number or null,
  "rate_per_km": number or null,
  "avg_speed_kmph": number (default 30),
  "mode": one of ["auto", "cab", "bike", "metro"] (default "auto"),
  "traffic": one of ["low", "normal", "heavy"] (default "normal"),
  "round_trip": boolean (default false)
}}

Rules:
- distance from "32km" -> 32
- rate from "18rs per km" -> 18
- speed from "30 km/h" -> 30
- if from X to Y pattern, extract source/destination
"""
        response = model.generate_content(prompt)
        # Clean markdown fences
        clean = response.text.strip().replace("```json", "").replace("```", "").strip()
        data = json.loads(clean)
        
        # Validate
        if data.get("distance_km") is None or data.get("rate_per_km") is None:
            print("[WARN] Gemini missed key fields, merging with regex")
            fallback = regex_extract(text)
            for k in ["distance_km", "rate_per_km"]:
                if data.get(k) is None and fallback.get(k):
                    data[k] = fallback[k]
        return data
        
    except Exception as e:
        print(f"[ERROR] Gemini extraction failed: {e}, falling back to regex")
        return regex_extract(text)

def extract_travel_info(text: str, use_gemini: bool = True) -> dict:
    if use_gemini:
        return gemini_extract(text)
    return regex_extract(text)
