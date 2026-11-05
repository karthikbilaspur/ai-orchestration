"""
Orchestrator V3 - LLM -> Calculator -> LLM
Now with Gemini explanation + auto output + history
"""
from .extractor_gemini import extract_travel_info
from .calculator import calculate_cost, calculate_time, estimate_budget
from .config import has_gemini_key, GEMINI_API_KEY, GEMINI_MODEL
import datetime, os, json

def gemini_explain(result: dict) -> str:
    if not has_gemini_key():
        return fallback_explain(result)
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(GEMINI_MODEL)
        prompt = "You are a friendly Bangalore travel assistant. Explain this: " + json.dumps(result, indent=2, default=str)
        resp = model.generate_content(prompt)
        return resp.text.strip()
    except Exception as e:
        print(f"[WARN] Gemini explain failed: {e}")
        return fallback_explain(result)

def fallback_explain(result: dict) -> str:
    src = result.get("source") or "your source"
    dest = result.get("destination") or "your destination"
    cost_info = result["cost_info"]
    time_info = result["time_info"]
    budget = result["budget"]
    rt = " (round trip)" if result.get("round_trip") else ""
    traffic_note = ""
    if time_info['traffic'] != 'normal':
        traffic_note = " With " + time_info['traffic'] + " traffic, effective speed is " + str(time_info['effective_speed']) + " km/h."
    
    lines = []
    lines.append(f"For your trip from {src} to {dest}{rt} ({cost_info['distance_charged']} km) by {cost_info['mode']}:")
    lines.append(f"- At Rs.{result['rate_per_km']}/km (mode adjusted), total cost = Rs.{cost_info['total_cost']} (base Rs.{cost_info['base_cost']}).")
    lines.append(f"- Time: ~{time_info['formatted']} ({time_info['hours_decimal']} hrs).{traffic_note}")
    lines.append(f"- Suggested budget: Rs.{budget['min_budget']} - Rs.{budget['max_budget']} (with {budget['buffer_percent']}% buffer).")
    lines.append("Tip: If traffic is heavy, consider metro for this route.")
    return "\n".join(lines)

def run_estimation(user_input: str, save_output: bool = True, use_gemini: bool = True) -> dict:
    extracted = extract_travel_info(user_input, use_gemini=use_gemini)
    if not extracted.get("distance_km") or not extracted.get("rate_per_km"):
        raise ValueError("Could not extract distance or rate. Example: Indiranagar to Airport 32km at 18rs/km speed 30 km/h")
    cost_info = calculate_cost(
        extracted["distance_km"], 
        extracted["rate_per_km"], 
        mode=extracted.get("mode", "auto"),
        round_trip=extracted.get("round_trip", False)
    )
    time_info = calculate_time(
        extracted["distance_km"], 
        extracted.get("avg_speed_kmph", 30),
        traffic=extracted.get("traffic", "normal"),
        round_trip=extracted.get("round_trip", False)
    )
    budget = estimate_budget(cost_info)
    final_result = {
        **extracted,
        "cost_info": cost_info,
        "time_info": time_info,
        "budget": budget,
        "timestamp": datetime.datetime.now().isoformat(),
        "input": user_input,
        "gemini_used": has_gemini_key() and use_gemini
    }
    final_result["explanation"] = gemini_explain(final_result)
    if save_output:
        os.makedirs("output", exist_ok=True)
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        with open(f"output/trip_{ts}.txt", "w", encoding="utf-8") as f:
            f.write(final_result["explanation"] + "\n\n--- RAW ---\n" + json.dumps(final_result, indent=2, default=str))
        with open(f"output/trip_{ts}.json", "w", encoding="utf-8") as f:
            json.dump(final_result, f, indent=2, default=str)
        import csv
        csv_path = "output/history.csv"
        is_new = not os.path.exists(csv_path)
        with open(csv_path, "a", newline="", encoding="utf-8") as cf:
            w = csv.DictWriter(cf, fieldnames=["timestamp","source","destination","distance_km","mode","total_cost","time_formatted"])
            if is_new: w.writeheader()
            w.writerow({
                "timestamp": final_result["timestamp"],
                "source": extracted.get("source"),
                "destination": extracted.get("destination"),
                "distance_km": extracted.get("distance_km"),
                "mode": extracted.get("mode"),
                "total_cost": cost_info["total_cost"],
                "time_formatted": time_info["formatted"]
            })
    return final_result
