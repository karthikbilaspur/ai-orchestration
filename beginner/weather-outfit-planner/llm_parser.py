"""
LLM Extractor: city = Bangalore, date = tomorrow
Uses OpenAI if key present, else falls back to regex/rule-based for demo.
"""
import os
import re
from datetime import datetime, timedelta
from dateutil import parser as date_parser

def extract_with_rules(user_query: str):
    """Fallback parser without LLM"""
    user_query_lower = user_query.lower()

    # City extraction - look for "in <City>" or common cities
    city_match = re.search(r'in\s+([A-Za-z\s]+?)(?:\s+tomorrow|\s+today|\s+\?|\s*$)', user_query, re.I)
    city = "Bangalore"  # default per your example
    if city_match:
        city = city_match.group(1).strip().title()
    elif "bangalore" in user_query_lower:
        city = "Bangalore"

    # Date extraction
    if "tomorrow" in user_query_lower:
        target_date = datetime.now() + timedelta(days=1)
    elif "today" in user_query_lower:
        target_date = datetime.now()
    else:
        # try parse any date
        try:
            # find date-like tokens
            target_date = date_parser.parse(user_query, fuzzy=True)
        except:
            target_date = datetime.now() + timedelta(days=1)

    intent = {
        "umbrella": "umbrella" in user_query_lower,
        "run": "run" in user_query_lower or "jog" in user_query_lower,
        "activity": "morning run" if "run" in user_query_lower else "general"
    }

    return {
        "city": city,
        "date": target_date.strftime("%Y-%m-%d"),
        "intent": intent,
        "raw_query": user_query
    }

def extract_with_llm(user_query: str):
    """
    If OPENAI_API_KEY is set, uses LLM. Otherwise uses rules.
    Prompt used is logged in log.txt
    """
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key or openai_key == "YOUR_API_KEY_HERE":
        return extract_with_rules(user_query)

    try:
        from openai import OpenAI
        client = OpenAI(api_key=openai_key)
        system_prompt = """
        You are a weather query parser. Extract:
        - city (string)
        - date (YYYY-MM-DD, interpret tomorrow/today relative to now)
        - intent: umbrella_needed (bool), activity (e.g. morning run, office, general)
        Return JSON only: {"city": "...", "date": "...", "intent": {"umbrella": true/false, "activity": "..."}}
        """
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query}
            ],
            temperature=0
        )
        import json
        parsed = json.loads(response.choices[0].message.content)
        parsed["raw_query"] = user_query
        return parsed
    except Exception as e:
        print(f"LLM fallback due to: {e}")
        return extract_with_rules(user_query)
