"""
LLM extraction layer: extracts ingredients + servings from natural language.
In production: uses OpenAI / Gemini. Here we have a fallback parser + LLM wrapper.
"""
import re
import json
from typing import Dict, List

# Simulated LLM prompt used:
EXTRACTION_PROMPT = """
You are a recipe parser. Given user input like "This pasta recipe is for 2 people: 200g pasta, 100ml cream. Make it for 5 people"
Extract JSON:
{
  "original_servings": 2,
  "new_servings": 5,
  "ingredients": [
    {"name": "pasta", "quantity": 200, "unit": "g"},
    {"name": "cream", "quantity": 100, "unit": "ml"}
  ]
}
Only return valid JSON.
"""

def extract_with_llm_mock(user_input: str) -> Dict:
    """
    Mock LLM extraction. If OPENAI_API_KEY set, you would call LLM here.
    For this project, we use robust regex fallback that mimics LLM JSON output.
    """
    # Find servings
    orig_match = re.search(r'for (\d+)\s*(people|servings|person)', user_input, re.I)
    new_match = re.search(r'(?:make it for|for)\s*(\d+)\s*(people|servings)?\s*(?:and|$)', user_input, re.I)
    # Get last occurrence as new servings if two numbers present
    all_serv = re.findall(r'for (\d+)', user_input, re.I)
    if len(all_serv) >= 2:
        original = int(all_serv[0])
        new = int(all_serv[-1])
    else:
        original = int(orig_match.group(1)) if orig_match else 2
        # second number in string after "make"
        m2 = re.search(r'make it for (\d+)', user_input, re.I)
        new = int(m2.group(1)) if m2 else original

    # Find ingredients: pattern like "200g pasta, 100ml cream"
    ing_pattern = r'(\d+\.?\d*)\s*(g|kg|ml|l|tsp|tbsp|cup|cups|pcs|piece|pieces)?\s*([a-zA-Z ]+?)(?:,|and|\.|$)'
    ingredients = []
    for qty, unit, name in re.findall(ing_pattern, user_input):
        ingredients.append({
            "name": name.strip().lower(),
            "quantity": float(qty),
            "unit": unit.lower() if unit else "unit"
        })

    return {
        "original_servings": original,
        "new_servings": new,
        "ingredients": ingredients,
        "scale_factor": round(new / original, 2) if original else 1
    }

if __name__ == "__main__":
    test = "This pasta recipe is for 2 people: 200g pasta, 100ml cream. Make it for 5 people and give me a shopping list."
    print(json.dumps(extract_with_llm_mock(test), indent=2))