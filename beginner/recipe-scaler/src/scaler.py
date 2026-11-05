"""
Python calculator: Pure logic, no LLM. Scales quantities.
Teaches separation of concerns: LLM for understanding, Python for math.
"""
from typing import List, Dict

def scale_ingredients(ingredients: List[Dict], original_servings: int, new_servings: int) -> List[Dict]:
    if original_servings <= 0:
        raise ValueError("Original servings must be > 0")
    factor = new_servings / original_servings
    scaled = []
    for ing in ingredients:
        scaled.append({
            "name": ing["name"],
            "quantity": round(ing["quantity"] * factor, 2),
            "unit": ing["unit"],
            "original_quantity": ing["quantity"]
        })
    return scaled, factor

def generate_shopping_list(scaled: List[Dict]) -> List[str]:
    return [f"{item['quantity']}{item['unit']} {item['name']}" for item in scaled]