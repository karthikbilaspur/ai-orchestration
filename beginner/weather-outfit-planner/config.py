import os
from dotenv import load_dotenv
load_dotenv()

# Get your free key from https://openweathermap.org/api
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "YOUR_API_KEY_HERE")
WEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5"
DEFAULT_CITY = "Bangalore"
