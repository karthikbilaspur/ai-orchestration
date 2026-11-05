"""
LLM formatting layer: Takes scaled data and returns clean human readable recipe + checklist.
"""
FORMATTING_PROMPT = """
You are a recipe formatter. Given scaled ingredients JSON, create:
1. A clean scaled recipe header
2. Step-by-step (keep simple)
3. A shopping checklist with [ ] checkboxes
Use friendly tone.
"""

def format_output(scaled_ingredients, original_servings, new_servings, factor, shopping_list) -> str:
    lines = []
    lines.append(f"# Scaled Recipe for {new_servings} people (was {original_servings}, x{factor:.2f})")
    lines.append("")
    lines.append("## Ingredients:")
    for ing in scaled_ingredients:
        lines.append(f"- {ing['quantity']}{ing['unit']} {ing['name']} (originally {ing['original_quantity']}{ing['unit']})")
    lines.append("")
    lines.append("## Shopping List:")
    for item in shopping_list:
        lines.append(f"- [ ] {item}")
    lines.append("")
    lines.append("Enjoy your cooking! 🍝")
    return "\n".join(lines)