import requests
from config import OPENWEATHER_API_KEY, WEATHER_BASE_URL

def get_air_quality(lat=12.9716, lon=77.5946):
    """Stretch: OpenWeather Air Pollution API"""
    if OPENWEATHER_API_KEY == "YOUR_API_KEY_HERE":
        return {"aqi": 2, "label": "Fair", "pm2_5": 18.5, "note": "mock data"}

    url = f"{WEATHER_BASE_URL.replace('/data/2.5','')}/data/2.5/air_pollution"
    # Correct endpoint: http://api.openweathermap.org/data/2.5/air_pollution
    url = "http://api.openweathermap.org/data/2.5/air_pollution"
    params = {"lat": lat, "lon": lon, "appid": OPENWEATHER_API_KEY}
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()["list"][0]
        aqi_map = {1: "Good", 2: "Fair", 3: "Moderate", 4: "Poor", 5: "Very Poor"}
        return {
            "aqi": data["main"]["aqi"],
            "label": aqi_map.get(data["main"]["aqi"], "Unknown"),
            "pm2_5": data["components"]["pm2_5"]
        }
    except Exception as e:
        return {"error": str(e)}
