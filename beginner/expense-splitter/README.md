# AI Expense Splitter & Tip Calculator

Idea: Solves group bills from a casual message like:
"We had dinner for 3480 rupees, including 18% GST. 4 of us splitting, but I want to add a 10% tip. How much each?"

## Orchestration Flow
1. User Message -> LLM Parser
2. LLM extracts -> total, gst%, tip%, num_people
3. -> Calculator Tool calculates GST, tip, final, per-person
4. -> LLM explains breakdown in simple English
5. Display result + log prompt exchange

## Files
- app.py - Main CLI app
- parser.py - Simulates LLM parsing + explanation
- calculator.py - Pure math tool
- test_app.py - Beginner tests
- log.txt - Prompt exchange log
- requirements.txt
- README.md

## How to Run
pip install -r requirements.txt
python app.py

## How to Test
python test_app.py

## Why Great for Beginners
- Learn LLM handling ambiguous numbers
- Separation: LLM for understanding, Python for accurate math
- Logging prompt exchanges

Example Output:
Total: Rs 3480 (includes 18% GST)
Base: Rs 2949.15 | GST: Rs 530.85
Tip (10%): Rs 348
Final Total: Rs 3828
Per Person (4): Rs 957
