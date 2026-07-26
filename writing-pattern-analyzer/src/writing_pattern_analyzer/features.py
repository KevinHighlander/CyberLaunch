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

def punctuation_counts(text: str) -> dict[str, int]:
    """Return raw counts for selected punctuation categories."""
    return {
        "periods": text.count("."),
        "commas": text.count(","),
        "semicolons": text.count(";"),
        "colons": text.count(":"),
        "question_marks": text.count("?"),
        "exclamation_marks": text.count("!"),
        "apostrophes": text.count("'") + text.count("’"),
        "hyphens": text.count("-"),
    }

def punctuation_rates(text: str) -> dict[str, float]:
    """Return punctuation occurrences per 100 words."""
    counts = punctuation_counts(text)
    total_words = count_words(text)

    if total_words == 0:
        return {name: 0.0 for name in counts}

    return {
        name: count / total_words * 100
        for name, count in counts.items()
    }

def count_sentences(text: str) -> int:
    """Return the number of detected sentences."""
    return len(tokenize_sentences(text))

def extract_features(text: str) -> dict[str, int | float]:
    """Extract the complete stylometric feature profile for text."""
    features = {
        "word_count": count_words(text),
        "unique_word_count": count_unique_words(text),
        "sentence_count": count_sentences(text),
        "vocabulary_richness": vocabulary_richness(text),
        "average_word_length": average_word_length(text),
        "average_sentence_length": average_sentence_length(text),
    }

    rates = punctuation_rates(text)

    for name, rate in rates.items():
        feature_name = f"{name}_per_100_words"
        features[feature_name] = rate

    return features

