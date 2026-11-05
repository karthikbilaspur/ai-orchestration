
import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

def has_gemini_key():
    return bool(GEMINI_API_KEY and GEMINI_API_KEY != "your_api_key_here")
