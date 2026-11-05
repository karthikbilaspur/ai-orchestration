"""Skill vocabulary + negation handling.

Why negation matters: the resume says "No AI experience." A naive keyword search
would find the word "AI" and wrongly credit the candidate with an AI skill.
"""
import re

# canonical name -> (category, [regex alternatives])
_TAXONOMY = {
    "Python": ("python", [r"python"]),
    "LLM": ("ai_llm", [r"llms?", r"large language models?", r"gpt(?:-?\d+)?", r"chatgpt",
                       r"openai", r"claude", r"gemini", r"langchain", r"langgraph",
                       r"llamaindex", r"rag", r"prompt engineering", r"hugging ?face",
                       r"transformers"]),
    "AI": ("ai_llm", [r"ai", r"artificial intelligence", r"generative ai", r"genai"]),
    "Machine Learning": ("ai_llm", [r"machine learning", r"ml", r"deep learning",
                                    r"neural networks?", r"nlp", r"natural language processing",
                                    r"scikit-?learn", r"sklearn", r"pytorch", r"tensorflow", r"keras"]),
    "SQL": ("relevant", [r"sql", r"mysql", r"postgres(?:ql)?", r"sqlite"]),
    "Git": ("relevant", [r"git", r"github"]),
    "Pandas": ("relevant", [r"pandas"]),
    "NumPy": ("relevant", [r"numpy"]),
    "Flask": ("relevant", [r"flask"]),
    "FastAPI": ("relevant", [r"fastapi"]),
    "Django": ("relevant", [r"django"]),
    "REST API": ("relevant", [r"rest(?:ful)? apis?"]),
    "Docker": ("relevant", [r"docker"]),
    "Streamlit": ("relevant", [r"streamlit"]),
    "Excel": ("other", [r"excel"]),
    "Java": ("other", [r"java"]),
    "JavaScript": ("other", [r"javascript"]),
    "C++": ("other", [r"c\+\+"]),
}


def _compile(patterns):
    body = "|".join(patterns)
    return re.compile(rf"(?<![A-Za-z0-9])(?:{body})(?![A-Za-z0-9])", re.I)


COMPILED = {name: (cat, _compile(p)) for name, (cat, p) in _TAXONOMY.items()}

_NEG = re.compile(
    r"\b(?:no|not|never|without|lack(?:s|ing)?|zero|none|haven'?t|hasn'?t|don'?t|doesn'?t|"
    r"(?:want|wants|plan|plans|hope|hopes|yet) to learn|interested in learning|"
    r"will learn|hoping to learn)\b", re.I)


def category(skill: str) -> str:
    return _TAXONOMY[skill][0] if skill in _TAXONOMY else "other"


def is_negated(text: str, pos: int) -> bool:
    """True if the match at `pos` is denied, e.g. 'No AI experience'."""
    start = max(text.rfind(c, 0, pos) for c in ".\n;!?")
    prefix = text[start + 1:pos]
    cut = max(prefix.rfind(","), prefix.rfind(":"))
    prefix = prefix[cut + 1:]
    return bool(_NEG.search(prefix[-35:]))


def find_skills(text: str):
    """Return (found, negated): found = {skill: first_position}, negated = set(skills)."""
    found, negated = {}, set()
    for canon, (_cat, rx) in COMPILED.items():
        for m in rx.finditer(text):
            if is_negated(text, m.start()):
                negated.add(canon)
            else:
                found.setdefault(canon, m.start())
    negated -= set(found)
    return found, negated


def affirmative(pattern: str, text: str) -> bool:
    """True if `pattern` appears in `text` at least once and is not negated."""
    return any(not is_negated(text, m.start())
               for m in re.finditer(pattern, text, re.I))


def job_requirements(jd: str) -> dict:
    found, _ = find_skills(jd)
    return {"python": "Python" in found,
            "ai_llm": any(category(s) == "ai_llm" for s in found)}
