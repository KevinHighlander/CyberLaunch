"""Tests for CLIM intelligence domains."""

from app.ontology.domains import get_all_domains, get_domain


def test_geopolitics_domain_exists() -> None:
    domain = get_domain("geopolitics")

    assert domain is not None
    assert domain.display_name == "Geopolitics"


def test_unknown_domain_returns_none() -> None:
    assert get_domain("does-not-exist") is None


def test_domains_are_registered() -> None:
    domains = get_all_domains()

    assert len(domains) >= 6