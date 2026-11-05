# AI Recipe Scaler & Grocery List Maker

Takes a recipe for N people and adjusts it for any number of people.

**Example:**
Input: "This pasta recipe is for 2 people: 200g pasta, 100ml cream. Make it for 5 people and give me a shopping list."

## Orchestration Flow (as per your idea)
1. **LLM extracts** -> ingredients + original servings + new servings (JSON)
2. **Python calculator** -> scales quantities: `200g * 2.5 = 500g`
3. **LLM formats** -> clean scaled recipe + shopping checklist
4. **Display + Auto-save** -> saves to `output/` folder automatically

## Why it's great
Teaches you structured JSON extraction from LLM - the most important skill for building AI apps. Separates LLM (understanding) from Python (math).

## Project Structure
```
recipe_scaler/
├── main.py               # Orchestrator
├── src/
│   ├── extractor.py      # LLM extraction -> JSON
│   ├── scaler.py         # Python math scaling
│   └── formatter.py      # LLM formatting
├── tests/
│   ├── test_scaler.py
│   └── test_extractor.py
├── output/               # Auto-generated on each run
├── requirements.txt
├── log.txt               # Prompts used
└── README.md
```

## How to Run
```bash
pip install -r requirements.txt
python main.py "This pasta recipe is for 2 people: 200g pasta, 100ml cream. Make it for 5 people"
# or just
python main.py
```
Every run creates `output/scaled_recipe_TIMESTAMP.txt` and `.json`

## Prompts Used (see log.txt)
- Extraction prompt for JSON
- Formatting prompt for friendly output