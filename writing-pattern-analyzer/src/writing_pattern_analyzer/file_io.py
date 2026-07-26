from pathlib import Path


def load_text_file(file_path: str | Path) -> str:
    """Load and return the contents of a UTF-8 text file."""
    path = Path(file_path)

    if path.suffix.lower() != ".txt":
        raise ValueError("Writing samples must be .txt files.")

    return path.read_text(encoding="utf-8")