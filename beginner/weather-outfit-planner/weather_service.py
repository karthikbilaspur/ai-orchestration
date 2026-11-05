import requests
from datetime import datetime
from config import OPENWEATHER_API_KEY, WEATHER_BASE_URL

class WeatherService:
    def __init__(self, api_key=OPENWEATHER_API_KEY):
        self.api_key = api_key

    def get_forecast(self, city: str, target_date: str):
        """Gets forecast for city. Uses /forecast endpoint and matches date."""
        if self.api_key == "YOUR_API_KEY_HERE":
            # MOCK for demo / testing without API key
            print("[MOCK MODE] No API key - returning sample data for Bangalore")
            return {
                "city": city,
                "date": target_date,
                "temp_c": 24.5,
                "feels_like_c": 26.0,
                "humidity": 78,
                "rain_prob": 30,
                "rain_mm": 2.1,
                "description": "light rain",
                "wind_kmh": 12,
                "source": "mock"
            }

        # Real API call
        # 1. Geocoding to forecast
        url = f"{WEATHER_BASE_URL}/forecast"
        params = {"q": city, "appid": self.api_key, "units": "metric"}
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        # Find closest forecast to target_date noon
        target_dt = datetime.strptime(target_date, "%Y-%m-%d")
        best = None
        for item in data["list"]:
            dt = datetime.fromtimestamp(item["dt"])
            if dt.date() == target_dt.date():
                best = item
                if dt.hour in [9,12]: # prefer morning/noon
                    break

        if not best:
            best = data["list"][0]

        return {
            "city": city,
            "date": target_date,
            "temp_c": best["main"]["temp"],
            "feels_like_c": best["main"]["feels_like"],
            "humidity": best["main"]["humidity"],
            "rain_prob": int(best.get("pop", 0)*100),
            "rain_mm": best.get("rain", {}).get("3h", 0),
            "description": best["weather"][0]["description"],
            "wind_kmh": round(best["wind"]["speed"]*3.6, 1),
            "source": "openweathermap"
        }
