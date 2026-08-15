"""Tests for watch-area classification."""

from app.watchlists.registry import classify_watch


def test_taiwan_watch_classification() -> None:
    result = classify_watch("China launches military exercises around Taiwan")
    assert result is not None
    assert result.display_name == "Taiwan Strait"


def test_korea_watch_classification() -> None:
    result = classify_watch("North Korea conducts ballistic missile launch")
    assert result is not None
    assert result.display_name == "Korean Peninsula"


def test_unrelated_story_has_no_watch() -> None:
    assert classify_watch("Local football club announces new coach") is None
