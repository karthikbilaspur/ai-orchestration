# AI Travel Time & Budget Estimator - Gemini Edition (V2)

Upgraded with Gemini API + 3 rounds of improvements.

## What's New in V2 (Gemini Upgrade)

### Round 1: Gemini API Integration
- `src/extractor_gemini.py` now calls `gemini-1.5-flash` with structured JSON prompt
- Falls back to regex if no API key
- `.env` based config via `src/config.py`

### Round 2: Smarter Calculator
- Supports modes: auto, cab (1.5x), bike (0.7x), metro (0.3x)
- Traffic factor: low (1.2x speed), normal (1x), heavy (0.6x)
- Round-trip detection: "round trip", "return"
- Waiting charges, min/max budget buffer

### Round 3: Orchestrator & UX
- Gemini also explains final result (not just extracts)
- Auto output: `output/trip_<timestamp>.txt` + `.json` + `history.csv`
- CLI with argparse: `--no-gemini`, `--interactive`
- History CSV for all trips

## Flow
```
User Input -> [Gemini Extracts: distance, rate, speed, source, dest, mode, traffic] 
          -> [Calculator: cost, time with factors] 
          -> [Gemini Explains]
          -> Saves to output/
```

## Setup

1. Get Gemini API key: https://aistudio.google.com/app/apikey
2. Setup:
```bash
cp .env.example .env
# Edit .env and paste your key
pip install -r requirements.txt
```

3. Run:
```bash
# With Gemini (if key set)
python main.py "I want to go from Indiranagar to Airport, 32km at 18rs/km, peak traffic, speed 30 km/h"

# Force regex fallback
python main.py --no-gemini "Indiranagar to Airport 32km at 18rs/km"

# Interactive
python main.py --interactive

# Cab round trip example
python main.py "Koramangala to Airport and back, 32km at 20rs/km by cab, heavy traffic speed 35 km/h"
```

## Example Outputs
- Auto 32km @18rs: ₹576, 1hr 4 mins
- Cab round-trip heavy traffic: cost doubles, time increases due to 0.6x speed factor

## Tests
```bash
pytest test_estimator.py -v
```

## Project Structure
```
├── main.py
├── .env.example
├── src/
│   ├── config.py
│   ├── extractor_gemini.py
│   ├── calculator.py
│   └── estimator.py
├── test_estimator.py
├── output/ (auto-generated)
└── log.txt
```

## Cost to Run
Gemini Flash is free-tier friendly. Regex fallback works offline with zero cost.
