
# AI Expense Splitter & Tip Calculator
### Beginner Friendly AI Orchestration Project (2-Hour Build)

**Multi-Step AI Orchestration:**
User Input (Natural Language) -> LLM Parser -> Python Calculator Tool -> LLM Explainer -> UI

#### Example
Input: "We had dinner for 3480 rupees, including 18% GST. 4 of us splitting, but I want to add a 10% tip. How much each?"
Output: Final total Rs.3828, Rs.957 each with full breakdown.

### Project Structure
- app.py - Main Streamlit app + Orchestrator (Layer 4 & 3)
- calculator.py - Pure Python Tool (Layer 2)
- prompts.py - All LLM prompts (Layer 1)
- test_calculator.py - Unit tests
- requirements.txt - Dependencies
- log.txt - Logs
- README.md

### How AI Orchestration Works
1. LLM Parse: Converts messy English into structured JSON
2. Tool Call: Python does reliable math (LLMs are bad at math!)
3. LLM Explain: Converts numbers back to friendly text
Pattern: LLM -> Tool -> LLM

### How to Run
pip install -r requirements.txt
streamlit run app.py

### Enable Real AI (Optional)
Get free Gemini API key from aistudio.google.com
Create .env file: GEMINI_API_KEY=your_key
In app.py, replace mock_llm_parser with real Gemini call using PARSER_PROMPT from prompts.py

### Run Tests
pytest test_calculator.py -v

### Learning Outcome
- Tool Calling / Function Calling
- Separating prompts from code
- Why we don't let LLM do math
- Streamlit for AI apps
- Unit testing for AI tools
