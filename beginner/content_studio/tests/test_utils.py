from src.utils import flesch_reading_ease, avg_sentence_length, keyword_density, extract_headings, top_keywords

def test_flesch_range():
    assert 0 <= flesch_reading_ease("The cat sat. The dog ran. Life is good.") <= 100
    assert flesch_reading_ease("") == 0.0

def test_avg_sentence_length():
    assert avg_sentence_length("Hello world. Hi there.") == 2.0

def test_keyword_density():
    assert keyword_density("cats cats cats", "cats") > 0
    assert keyword_density("hello", "missing") == 0.0

def test_extract_headings():
    assert extract_headings("# Title\n## Section") == ["Title", "Section"]

def test_top_keywords():
    assert "gardening" in top_keywords("gardening gardening gardening plants soil", 3)
