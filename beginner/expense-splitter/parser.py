
# LLM Parser (Simulated) - This is where the AI part happens.
# In real project, you'd call OpenAI/Gemini API here.
import re

def llm_parse_expense(text):
    text_lower = text.lower()
    total = 0.0
    rupees_match = re.search(r'([0-9]+(?:\.[0-9]+)?)\s*(?:rupees|rs\b)', text_lower)
    total_match = re.search(r'(?:rs\.?|rupees|inr|total|bill)?\s*([0-9]+(?:\.[0-9]+)?)', text_lower)
    if rupees_match:
        total = float(rupees_match.group(1))
    elif total_match:
        total = float(total_match.group(1))

    gst_match = re.search(r'(\d+(?:\.\d+)?)\s*%\s*(?:gst|tax|vat)', text_lower)
    if not gst_match:
        gst_match = re.search(r'(?:gst|tax).*?(\d+(?:\.\d+)?)\s*%', text_lower)
    gst = float(gst_match.group(1)) if gst_match else 0.0

    tip_match = re.search(r'(\d+(?:\.\d+)?)\s*%\s*tip', text_lower)
    if not tip_match:
        tip_match = re.search(r'tip.*? (\d+(?:\.\d+)?)\s*%', text_lower)
    tip = float(tip_match.group(1)) if tip_match else 0.0

    people_match = re.search(r'(\d+)\s*(?:of us|people|person|friends|split)', text_lower)
    if people_match:
        num_people = int(people_match.group(1))
    else:
        num_people = 1

    return {"total": total, "gst_percent": gst, "tip_percent": tip, "num_people": num_people}

def llm_explain_breakdown(calc_result):
    return f"""
Here's your bill breakdown in simple English:

You had a total bill of Rs {calc_result['total_with_gst']} which already includes {calc_result['gst_percent']}% GST.
- Base food amount was Rs {calc_result['base_amount']}
- GST amount is Rs {calc_result['gst_amount']}

You wanted to add a {calc_result['tip_percent']}% tip, which is Rs {calc_result['tip_amount']}.
So final total to pay is Rs {calc_result['final_total']}.

You are {calc_result['num_people']} people splitting it.
Each person pays: Rs {calc_result['per_person']}
""".strip()
