"""
Main orchestration: LLM extracts -> Python calculator -> LLM formats -> Display + Auto-save to output/
"""
import os, datetime, json, pathlib
from src.extractor import extract_with_llm_mock
from src.scaler import scale_ingredients, generate_shopping_list
from src.formatter import format_output

def run(recipe_input: str):
    print(f">> Input: {recipe_input}")
    # Step 1: LLM Extract
    extracted = extract_with_llm_mock(recipe_input)
    print(">> Extracted:", json.dumps(extracted, indent=2))

    # Step 2: Python Calculator
    scaled, factor = scale_ingredients(
        extracted["ingredients"],
        extracted["original_servings"],
        extracted["new_servings"]
    )

    # Step 3: Shopping list
    shopping = generate_shopping_list(scaled)

    # Step 4: LLM Format
    formatted = format_output(scaled, extracted["original_servings"], extracted["new_servings"], factor, shopping)

    print("\n" + formatted)

    # Auto-save to output/
    out_dir = pathlib.Path("output")
    out_dir.mkdir(exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = out_dir / f"scaled_recipe_{timestamp}.txt"
    out_json = out_dir / f"scaled_recipe_{timestamp}.json"

    out_path.write_text(formatted)
    out_json.write_text(json.dumps({"input": recipe_input, "extracted": extracted, "scaled": scaled, "factor": factor}, indent=2))

    print(f"\n[SAVED] Text: {out_path}")
    print(f"[SAVED] JSON: {out_json}")
    return formatted

if __name__ == "__main__":
    # Default example
    example = "This pasta recipe is for 2 people: 200g pasta, 100ml cream. Make it for 5 people and give me a shopping list."
    # Allow CLI arg
    import sys
    user_input = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else example
    run(user_input)