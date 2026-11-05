
from parser import llm_parse_expense, llm_explain_breakdown
from calculator import calculate_bill
import datetime

LOG_FILE = "log.txt"

def log_exchange(user_input, parsed_data, calc_result, explanation):
    with open(LOG_FILE, "a", encoding="utf-8") as log:
        log.write(f"\n=== {datetime.datetime.now()} ===\n")
        log.write(f"USER PROMPT: {user_input}\n")
        log.write(f"LLM PARSE -> Calculator Input: {parsed_data}\n")
        log.write(f"Calculator Tool -> Output: {calc_result}\n")
        log.write(f"LLM Explanation -> User: {explanation[:200]}...\n")
        log.write("-"*50 + "\n")

def run_splitter(user_message):
    print(f"\n>> User says: {user_message}")
    print("[LLM] Parsing your message...")
    parsed = llm_parse_expense(user_message)
    print(f"[LLM] Got: {parsed}")
    print("[Tool] Calculating...")
    result = calculate_bill(parsed["total"], parsed["gst_percent"], parsed["tip_percent"], parsed["num_people"])
    print(f"[Tool] Result: {result}")
    print("[LLM] Explaining breakdown...")
    explanation = llm_explain_breakdown(result)
    print("\n" + explanation)
    log_exchange(user_message, parsed, result, explanation)
    return result

if __name__ == "__main__":
    open(LOG_FILE, "w").write("AI Expense Splitter - Prompt Exchange Log\n")
    print("=== AI Expense Splitter & Tip Calculator ===")
    print("Example: We had dinner for 3480 rupees, including 18% GST. 4 of us splitting, but I want to add a 10% tip. How much each?\n")
    while True:
        msg = input("Enter your bill message (or 'exit'): ")
        if msg.lower() == "exit":
            break
        if not msg.strip():
            continue
        run_splitter(msg)
