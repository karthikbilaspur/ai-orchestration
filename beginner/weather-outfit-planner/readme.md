# AI Weather Outfit Planner

**Idea:** LLM + Weather API + Logic  
Input: "Should I carry an umbrella in Bangalore tomorrow? And what should I wear for a morning run?"

### Orchestration Flow
1. **LLM extracts** -> city = Bangalore, date = tomorrow, intent = {umbrella, morning run}
2. **Call Weather API tool** -> OpenWeatherMap forecast (temp, rain %, description, wind)
3. **(Stretch) Call Air Quality API** -> AQI for health-aware run recommendation
4. **Send forecast back to LLM/Logic** -> rule-based outfit + umbrella decision
5. **Display + Auto Save** -> Saves JSON + TXT to `output/` folder automatically

### Project Structure
```
ai_weather_outfit_planner/
├── py files first:
│   ├── main.py (orchestrator CLI)
│   ├── llm_parser.py (LLM extraction with regex fallback)
│   ├── weather_service.py (OpenWeatherMap wrapper + mock mode)
│   ├── outfit_logic.py (temp/rain -> outfit rules)
│   ├── air_quality.py (stretch AQI)
│   └── config.py (env keys)
├── tests/test_planner.py
├── output/ (auto-created on each run)
├── log.txt (prompts used)
├── requirements.txt
└── readme.md
```

### Setup
1. `pip install -r requirements.txt`
2. Get free API key from openweathermap.org and set in .env:
```
OPENWEATHER_API_KEY=your_key
OPENAI_API_KEY=optional_for_llm_parser
```
3. If no keys, app runs in MOCK mode (perfect for demo).

### Run
```bash
python main.py
# or
python main.py "Should I carry umbrella in Bangalore tomorrow?"
```

Each run auto-creates `output/result_<timestamp>.json` and `.txt`

### Tools
- LLM: OpenAI GPT-4o-mini (or rule fallback)
- Weather API: OpenWeatherMap
- Python: requests, dotenv, dateutil

### Example Output
> 30% rain, 24.5°C, light rain. Wear: moisture-wicking t-shirt, running shorts, running shoes. Carry umbrella / light rain jacket.
