import re


def tokenize_words(text: str) -> list[str]:
    """Return lowercase word tokens with surrounding punctuation removed."""
    pattern = r"[A-Za-z]+(?:['’-][A-Za-z]+)*"
    return re.findall(pattern, text.lower())


def count_words(text: str) -> int:
    """Return the number of word tokens in text."""
    return len(tokenize_words(text))

def count_unique_words(text: str) -> int:
    """Return the number of distinct lowercase word tokens."""
    tokens = tokenize_words(text)
    return len(set(tokens))


def vocabulary_richness(text: str) -> float:
    """Return the proportion of word tokens that are unique."""
    tokens = tokenize_words(text)

    if not tokens:
        return 0.0

    return len(set(tokens)) / len(tokens)