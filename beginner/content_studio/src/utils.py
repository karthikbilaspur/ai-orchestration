"""Readability + SEO helpers. Pure functions = easy to unit test."""
import re
from collections import Counter

def word_count(text: str) -> int:
    return len(text.split())

def sentence_count(text: str) -> int:
    parts = [s for s in re.split(r'[.!?]+', text) if s.strip()]
    return max(1, len(parts))

def avg_sentence_length(text: str) -> float:
    return round(word_count(text) / sentence_count(text), 1)

def flesch_reading_ease(text: str) -> float:
    """Simplified Flesch Reading Ease. Higher = easier. 60-70 = plain English."""
    words = text.split()
    if not words:
        return 0.0
    sentences = sentence_count(text)
    syllables = sum(_syllables(w) for w in words)
    score = 206.835 - 1.015 * (len(words)/sentences) - 84.6 * (syllables/len(words))
    return round(max(0, min(100, score)), 1)

def _syllables(word: str) -> int:
    word = re.sub(r'[^a-z]', '', word.lower())
    if not word:
        return 0
    groups = re.findall(r'[aeiouy]+', word)
    count = len(groups)
    if word.endswith('e') and count > 1:
        count -= 1
    return max(1, count)

def extract_headings(markdown: str) -> list[str]:
    return [l.strip('# ').strip() for l in markdown.splitlines() if l.strip().startswith('#')]

def keyword_density(text: str, keyword: str) -> float:
    if not keyword or not text:
        return 0.0
    words = len(text.split())
    hits = text.lower().count(keyword.lower())
    return round((hits / max(1, words)) * 100, 2)

def top_keywords(text: str, n: int = 8) -> list[str]:
    stop = set("the a an and or of to in on for with is are was were be by at as it this that from you your we our can will".split())
    words = [re.sub(r'[^a-z]', '', w.lower()) for w in text.split()]
    words = [w for w in words if len(w) > 3 and w not in stop]
    return [w for w, _ in Counter(words).most_common(n)]
