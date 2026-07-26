from pathlib import Path

from .features import extract_features
from .file_io import load_text_file


STYLE_FEATURES = (
    "vocabulary_richness",
    "average_word_length",
    "average_sentence_length",
    "periods_per_100_words",
    "commas_per_100_words",
    "semicolons_per_100_words",
    "colons_per_100_words",
    "question_marks_per_100_words",
    "exclamation_marks_per_100_words",
    "apostrophes_per_100_words",
    "hyphens_per_100_words",
)

def calculate_feature_similarity(
    value_a: int | float,
    value_b: int | float,
) -> float:
    """Return a scale-independent similarity from 0.0 to 1.0."""
    sample_a = float(value_a)
    sample_b = float(value_b)

    if sample_a < 0 or sample_b < 0:
        raise ValueError("Feature values cannot be negative.")

    if sample_a == 0 and sample_b == 0:
        return 1.0

    difference = abs(sample_a - sample_b)
    return 1.0 - difference / (sample_a + sample_b)

def compare_feature_values(
    value_a: int | float,
    value_b: int | float,
) -> dict[str, float]:
    """Return two feature values and their absolute difference."""
    sample_a = float(value_a)
    sample_b = float(value_b)

    return {
        "sample_a": sample_a,
        "sample_b": sample_b,
        "absolute_difference": abs(sample_a - sample_b),
        "similarity": calculate_feature_similarity(sample_a, sample_b),
}   
def calculate_feature_similarity(
    value_a: int | float,
    value_b: int | float,
) -> float:
    """Return a scale-independent similarity from 0.0 to 1.0."""
    sample_a = float(value_a)
    sample_b = float(value_b)

    if sample_a < 0 or sample_b < 0:
        raise ValueError("Feature values cannot be negative.")

    if sample_a == 0 and sample_b == 0:
        return 1.0

    difference = abs(sample_a - sample_b)
    return 1.0 - difference / (sample_a + sample_b)

def compare_profiles(
    profile_a: dict[str, int | float],
    profile_b: dict[str, int | float],
) -> dict[str, dict[str, float]]:
    """Compare the stylistic measurements in two feature profiles."""
    comparison = {}

    for feature_name in STYLE_FEATURES:
        comparison[feature_name] = compare_feature_values(
            profile_a[feature_name],
            profile_b[feature_name],
        )

    return comparison


def compare_texts(
    text_a: str,
    text_b: str,
) -> dict[str, dict[str, float]]:
    """Extract and compare features from two pieces of text."""
    profile_a = extract_features(text_a)
    profile_b = extract_features(text_b)
    return compare_profiles(profile_a, profile_b)


def compare_files(
    file_path_a: str | Path,
    file_path_b: str | Path,
) -> dict[str, dict[str, float]]:
    """Load and compare two UTF-8 text files."""
    text_a = load_text_file(file_path_a)
    text_b = load_text_file(file_path_b)
    return compare_texts(text_a, text_b)

