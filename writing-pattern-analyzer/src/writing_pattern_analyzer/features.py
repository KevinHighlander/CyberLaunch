import re


def tokenize_words(text: str) -> list[str]:
    """Return lowercase word tokens with surrounding punctuation removed."""
    pattern = r"[A-Za-z]+(?:['’-][A-Za-z]+)*"
    return re.findall(pattern, text.lower())

def tokenize_sentences(text: str) -> list[str]:
    """Split text into nonempty sentences using ending punctuation."""
    pieces = re.split(r"[.!?]+", text)
    return [piece.strip() for piece in pieces if piece.strip()]

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

def average_sentence_length(text: str) -> float:
    """Return the average number of words per sentence."""
    sentences = tokenize_sentences(text)

    if not sentences:
        return 0.0

    word_counts = [count_words(sentence) for sentence in sentences]
    return sum(word_counts) / len(word_counts)

def average_word_length(text: str) -> float:
    """Return the average number of letters per word token."""
    tokens = tokenize_words(text)

    if not tokens:
        return 0.0

    total_letters = 0

    for token in tokens:
        for character in token:
            if character.isalpha():
                total_letters += 1

    return total_letters / len(tokens)

