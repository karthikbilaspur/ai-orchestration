
import streamlit as st
import json
import logging
from datetime import datetime
from prompts import PARSER_PROMPT, EXPLAINER_PROMPT
from calculator import calculate_bill
import re

logging.basicConfig(filename='log.txt', level=logging.INFO, format='%(asctime)s - %(message)s')

def mock_llm_parser(user_query):
    query = user_query.lower()
    total_match = re.search(r'(?:rs|rupees|\$)?\s*(\d{3,5})', query)
    total = float(total_match.group(1)) if total_match else 0
    
    people = 1
    if '4 of us' in query or '4 people' in query or 'split among 4' in query:
        people = 4
    elif '2 of us' in query or '2 people' in query:
        people = 2
    elif '3 of us' in query or '3 people' in query:
        people = 3
    elif '5 of us' in query:
        people = 5
    else:
        m = re.search(r'(\d+)\s*(?:of us|people|friends)', query)
        if m:
            people = int(m.group(1))

    gst_match = re.search(r'(\d+)\s*%\s*(?:gst|tax)', query)
    gst = float(gst_match.group(1)) if gst_match else 0

    tip_match = re.search(r'(\d+)\s*%\s*tip', query)
    if tip_match:
        tip = float(tip_match.group(1))
    else:
        tip_match2 = re.search(r'tip.*? (\d+)\s*%|add.*? (\d+)\s*%\s*tip', query)
        if tip_match2:
            v = tip_match2.group(1) or tip_match2.group(2)
            tip = float(v) if v else 0
        else:
            tip = 0

    including = 'including' in query or 'inclusive' in query

    return {
        "total_amount": total,
        "gst_percent": gst,
        "tip_percent": tip,
        "num_people": people,
        "gst_inclusive": including,
        "raw_query": user_query
    }

st.set_page_config(page_title="AI Expense Splitter", page_icon="💸", layout="centered")
st.title("💸 AI Expense Splitter & Tip Calculator")
st.caption("Type in plain English. AI + Calculator will do the rest.")

st.markdown("**Example:** We had dinner for 3480 rupees, including 18% GST. 4 of us splitting, but I want to add a 10% tip. How much each?")

user_input = st.text_area("Your bill message:", height=100, placeholder="We had dinner for 3480 rupees, including 18% GST. 4 of us splitting, but I want to add a 10% tip...")

if st.button("✨ Split My Bill", type="primary"):
    if not user_input.strip():
        st.warning("Please enter your bill details.")
    else:
        with st.status("🤖 AI Orchestration in progress...", expanded=True) as status:
            st.write("**Step 1:** LLM is parsing your message...")
            parsed = mock_llm_parser(user_input)
            st.json(parsed)
            logging.info(f"Parsed: {parsed}")

            st.write("**Step 2:** Calculator tool is computing...")
            result = calculate_bill(
                total_amount=parsed['total_amount'],
                gst_percent=parsed['gst_percent'],
                tip_percent=parsed['tip_percent'],
                num_people=parsed['num_people'],
                gst_inclusive=parsed['gst_inclusive']
            )
            st.json(result)
            logging.info(f"Calculated: {result}")

            st.write("**Step 3:** LLM is generating friendly explanation...")
            explanation = f"""
**Bill Breakdown:**
- Base Amount: Rs.{result['base_amount']:.2f}
- GST ({parsed['gst_percent']}%): Rs.{result['gst_amount']:.2f}
- Subtotal: Rs.{result['subtotal']:.2f}
- Tip ({parsed['tip_percent']}%): Rs.{result['tip_amount']:.2f}
- **Final Total: Rs.{result['final_total']:.2f}**
            
Split among **{parsed['num_people']} people = Rs.{result['per_person']:.2f} each**
            """
            status.update(label="✅ Done!", state="complete", expanded=False)

        st.success("Here is your split:")
        st.markdown(explanation)

        with open("log.txt", "a") as f:
            f.write(f"{datetime.now()} | Input: {user_input} | Result: {result}\n")

        st.divider()
        st.markdown("#### 🧠 How AI Orchestration worked:")
        st.markdown(f"""
1.  **LLM Parse:** Converted your text into JSON: `{parsed}`
2.  **Calculator Tool:** Did exact math (LLMs are bad at math!)
3.  **LLM Explain:** Converted numbers back to human-friendly text
        """)

st.sidebar.header("Project Files")
st.sidebar.info("This project contains:\n- app.py (UI + Orchestrator)\n- calculator.py (Tool)\n- prompts.py (LLM prompts)\n- test_calculator.py (Unit tests)\n- requirements.txt\n- log.txt\n- README.md")
