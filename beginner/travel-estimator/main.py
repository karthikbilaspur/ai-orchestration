"""
AI Travel Estimator - Gemini Edition
Usage:
  python main.py "Indiranagar to Airport 32km at 18rs/km speed 30"
  python main.py --no-gemini "32km at 20rs/km"
  python main.py --interactive
"""
import argparse
from src.estimator import run_estimation
from src.config import has_gemini_key

def main():
    parser = argparse.ArgumentParser(description="AI Travel Time & Budget Estimator (Gemini)")
    parser.add_argument("query", nargs="*", help="Travel query in natural language")
    parser.add_argument("--no-gemini", action="store_true", help="Force regex fallback")
    parser.add_argument("--interactive", action="store_true", help="Interactive mode")
    args = parser.parse_args()

    print(f"Gemini API: {'ACTIVE' if has_gemini_key() and not args.no_gemini else 'FALLBACK (regex)'}")

    if args.interactive or not args.query:
        user_input = input("Enter travel query: ")
    else:
        user_input = " ".join(args.query)

    try:
        result = run_estimation(user_input, save_output=True, use_gemini=not args.no_gemini)
        print("\n" + "="*50)
        print("ESTIMATION RESULT")
        print("="*50)
        print(result["explanation"])
        print("\nSaved to output/ (txt + json + history.csv)")
    except Exception as e:
        print(f"Error: {e}")
        print("Tip: Try 'Go from Indiranagar to Airport, 32km at 18rs/km, speed 30 km/h'")

if __name__ == "__main__":
    main()
