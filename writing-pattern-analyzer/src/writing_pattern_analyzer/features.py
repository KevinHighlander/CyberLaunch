import re


def tokenize_words(text: str) -> list[str]:
    """Return lowercase word tokens with surrounding punctuation removed."""
    pattern = r"[A-Za-z]+(?:['’-][A-Za-z]+)*"
    return re.findall(pattern, text.lower())


def count_words(text: str) -> int:
    """Return the number of word tokens in text."""
    return len(tokenize_words(text))